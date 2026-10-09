"""Create private synthetic CI configuration. Never reads a cloud connection."""
import json
import os
import re
import secrets
from pathlib import Path

if os.environ.get('GITHUB_ACTIONS') != 'true': raise RuntimeError('Dedicated GitHub CI only')
run = os.environ.get('GITHUB_RUN_ID', '')
if not run.isdigit(): raise RuntimeError('CI run identifier required')
password = os.environ.get('EBT_SQL_PASSWORD', '')
if not re.fullmatch(r'EbtQa_[0-9]+!X', password): raise RuntimeError('Synthetic CI SQL password required')
root = Path(__file__).resolve().parents[2]
runtime = root/'tmp/runtime'; runtime.mkdir(parents=True,exist_ok=True)
secret = secrets.token_hex(32)
database = 'EbtPlatformQa_Ci_'+run
config = {'ConnectionStrings':{'Platform':f'Server=localhost;Database={database};User Id=sa;Password={password};Encrypt=True;TrustServerCertificate=True'},
          'Platform':{'KeyPath':str(runtime/'keys'),'RunWorkers':True},
          'Qa':{'Password':'EbtQa9!'+secret[:24],'AccessFile':str(runtime/'qa-access.json'),'SqlReport':str(root/'evidencias/generic_sql_qa.json'),'AppSecret':secret,'VerifyToken':'verify-'+secret},
          'Documents':{'ScannerEnabled':False}}
(runtime/'local-config.json').write_text(json.dumps(config),encoding='utf-8')
print('PASS Dedicated synthetic CI configuration prepared; no cloud credential.')
