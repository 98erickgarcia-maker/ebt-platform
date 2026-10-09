"""Prepare synthetic-only local fixtures without loading real provider credentials."""
import json, subprocess, uuid
from pathlib import Path
root=Path(__file__).resolve().parents[1]
config=json.loads((root/'tmp/runtime/local-config.json').read_text(encoding='utf-8-sig'))
if config['ConnectionStrings']['Platform']!='Server=localhost;Database=EbtPlatformQa_20261007Migrated;Integrated Security=True;Encrypt=True;TrustServerCertificate=True':raise RuntimeError('Unexpected fixture')
access=json.loads((root/'tmp/runtime/qa-access.json').read_text(encoding='utf-8-sig'))
config['WazVox']={'Enabled':True,'Apps':{'wz-qa':{'WorkspaceId':'workspace-qa','SigningSecret':config['Qa']['AppSecret']}},'Connections':{}}
config['Meta']={'Enabled':False}
(root/'tmp/runtime/wazvox-qa-config.json').write_text(json.dumps(config),encoding='utf-8')
for field,phone in [('tenantA','wz-qa-A'),('tenantB','wz-qa-B')]:
 tenant=str(uuid.UUID(access[field]))
 query=f"""SET NOCOUNT ON; EXEC sp_set_session_context @key=N'ebt_system',@value=1;
 INSERT INTO ebt_connect.Connections(TenantId,Id,Version,Name,Provider,AppKey,AccountId,PhoneNumberId,SecretRef,Portfolio,OperatorId,Active)
 SELECT m.TenantId,NEWID(),1,N'QA WazVox synthetic','wazvox','wz-qa','wz-qa-account','{phone}','no-network-key','principal',m.UserId,1
 FROM ebt_connect.Memberships m JOIN ebt_connect.Users u ON u.Id=m.UserId
 WHERE m.TenantId='{tenant}' AND u.Email='admin@ebt.example' AND m.Role='admin'
 AND NOT EXISTS(SELECT 1 FROM ebt_connect.Connections c WHERE c.TenantId=m.TenantId AND c.AppKey='wz-qa');"""
 subprocess.run(['sqlcmd','-S','localhost','-E','-C','-b','-d','EbtPlatformQa_20261007Migrated','-Q',query],check=True)
print('Synthetic WazVox fixture ready; no real API key loaded.')
