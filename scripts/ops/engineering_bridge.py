"""Loopback-only authenticated n8n bridge; fixed service wakeups, no shell/model/key access."""
import hmac
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Bridge:
    def __init__(self, checkpoint, token, run=None, now=time.time):
        if len(token) < 40:
            raise ValueError('strong_bridge_token_required')
        self.path, self.token, self.now = Path(checkpoint), token, now
        self.run = run or (lambda argv: subprocess.run(argv, check=True, timeout=10,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        self.lock, self.last_tick = threading.Lock(), None

    def status(self):
        data = json.loads(self.path.read_text(encoding='utf-8'))
        states = {'quota','daily_limit','task_verified','proposal_ready','running','starting',
            'blocked','auth','awaiting_sync','preparing_sync','checks_failed','scope_violation',
            'task_scope_violation','task_file_limit','dependency_missing','invalid_model_policy'}
        state = data.get('status')
        if state not in states:
            state = 'blocked'
        module = data.get('current_task', 'unassigned')
        if not isinstance(module,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',module):
            module = 'unassigned'
        cooldown = data.get('cooldown_until', 0)
        if not isinstance(cooldown,(float,int)):
            raise ValueError('invalid_checkpoint')
        return dict(state=state, task=module, waitSeconds=max(0,int(cooldown-self.now())),
            completedCount=len(data.get('completed', [])),
            callsToday=data.get('calls_today',0), observedAtUtc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(self.now())))

    def handle(self, method, path, token, body):
        if not hmac.compare_digest(token, self.token):
            return 401, {'error':'unauthorized'}
        if len(body)>1024:
            return 413, {'error':'body_too_large'}
        if (method,path) not in {('GET','/api/status'),('POST','/api/tick')}:
            return 404, {'error':'not_found'}
        try:
            state = self.status()
            if method == 'GET':
                return 200,state
            if body and json.loads(body) != {}:
                return 400,{'error':'empty_object_required'}
            with self.lock:
                if self.last_tick is not None and self.now()-self.last_tick < 15:
                    return 429,{'error':'tick_throttled'}
                self.run(['systemctl','start','--no-block','ebt-engineering-watch.service'])
                queue = state['waitSeconds']==0 and state['state'] in {
                    'quota','daily_limit','task_verified','starting','awaiting_sync'}
                if queue:
                    self.run(['systemctl','start','--no-block','ebt-engineering-runner.service'])
                self.last_tick = self.now()
                return 202,dict(state,runnerQueued=queue,observerQueued=True)
        except json.JSONDecodeError:
            return 400,{'error':'invalid_json'}
        except (OSError, ValueError, TypeError, subprocess.SubprocessError):
            return 503,{'error':'controller_unavailable'}


def main():
    app=Bridge('/var/lib/ebt-engineering/state/checkpoint.json',os.environ['EBT_BRIDGE_TOKEN'])
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self): self.respond()
        def do_POST(self): self.respond()
        def respond(self):
            try:
                length=int(self.headers.get('Content-Length','0'))
                if length<0 or length>1024:
                    status,data=413,{'error':'body_too_large'}
                else:
                    status,data=app.handle(self.command,self.path,
                        self.headers.get('X-EBT-Bridge-Token',''),self.rfile.read(length))
            except ValueError:
                status,data=400,{'error':'invalid_length'}
            raw=json.dumps(data).encode()
            self.send_response(status)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store')
            self.end_headers();self.wfile.write(raw)
        def log_message(self,*args): pass
    ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()


if __name__=='__main__':main()
