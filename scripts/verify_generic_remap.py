"""Validate generic architecture mapping without claiming product execution."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
model = json.loads((ROOT / 'planejamento/remapeamento_plataforma_generica.json').read_text(encoding='utf-8'))
assert model['project'] == 'EBT Platform'
assert model['budget']['delivery_h'] == 180 and model['budget']['reserve_h'] == 20
assert model['budget']['actual_h'] is None
assert [x['id'] for x in model['core']] == [f'C{i}' for i in range(14)]
assert hashlib.sha256((ROOT / model['source']).read_bytes()).hexdigest() == model['source_sha256']
assert set(model['products']) == {'Connect', 'Flow', 'Portal', 'Contracts', 'Sst', 'Legislative'}
for item in model['core']:
    assert item['next_gap'] and item['evidence_for_new_changes'] is None
    if item['source_path']:
        assert (ROOT / item['source_path']).is_file(), item['source_path']
        assert item['current_state'] == 'codigo_no_recorte_nao_core_completo'
    else:
        assert item['current_state'] == 'planejado_nao_implementado'
print('PASS C0-C13, 6 produtos, fonte/hash e 180h+20h; remapeamento documental, sem promover gates.')
