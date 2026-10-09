"""Authenticated generic catalog on a fresh localhost SQL fixture. No external account."""
import http.cookiejar
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
port = int(os.environ.get('EBT_QA_PORT', '5186'))
if not 1024 <= port <= 65535: raise RuntimeError('Invalid QA port')
BASE = f'http://127.0.0.1:{port}'
access = json.loads((ROOT/'tmp/runtime/qa-access.json').read_text(encoding='utf-8-sig'))
config = json.loads((ROOT/'tmp/runtime/local-config.json').read_text(encoding='utf-8-sig'))
if not config['ConnectionStrings']['Platform'].startswith('Server=localhost;Database=EbtPlatformQa_'):
    raise RuntimeError('Exclusive localhost synthetic fixture required')

def client(): return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def request(c, path, method='GET', data=None, expected=200):
    headers = {}
    if method != 'GET':
        token = request(c, '/api/security/csrf')['token']
        headers.update({'X-CSRF-TOKEN': token, 'Content-Type': 'application/json'})
    try:
        with c.open(urllib.request.Request(BASE+path, json.dumps(data).encode() if data is not None else None, headers, method=method), timeout=30) as response:
            assert response.status == expected
            raw = response.read(); return json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        assert error.code == expected, (path, error.code, expected)
        return None

route = '/api/platform/v1/capabilities'
request(client(), route, expected=401)
print('PASS Unauthenticated catalog denied')
for email, role in [('admin@ebt.example','admin'),('consulta@ebt.example','reader')]:
    c = client(); request(c, '/api/auth/login', 'POST', {'email':email,'password':access['password']})
    if role == 'admin': request(c, '/api/auth/context/'+access['tenantA'], 'POST', expected=204)
    result = request(c, route)
    assert result['platform'] == 'EBT Platform' and result['product'] == 'Connect'
    assert not any(m['key'] in {'sst','clinical','workflow','builder'} for m in result['modules'])
    if role == 'reader': assert all(m['access'] == 'read' for m in result['modules'])
    else:
        before = result['tenantId']; request(c, '/api/auth/context/'+access['tenantB'], 'POST', expected=204)
        assert request(c, route)['tenantId'] == access['tenantB'] != before
    print('PASS Authenticated catalog and trusted tenant for', role)
report = {'passed':True,'scope':'localhost synthetic SQL, generic catalog only','cases':3,'production':False}
(ROOT/'evidencias/generic_platform_qa.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
