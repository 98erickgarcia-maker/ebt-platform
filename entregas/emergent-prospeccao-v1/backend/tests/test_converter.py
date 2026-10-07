import json
from convert_csv import convert


def test_converter_filters_uf_and_cnae_without_losing_leading_zero(tmp_path):
    source=tmp_path/'base.csv'
    source.write_text('cnpj;company_name;city;uf;cnae;status\n00123456000100;Empresa A;São Paulo;SP;6201501;02\n00123456000200;Empresa B;Vitória;ES;6201501;02\n',encoding='utf-8')
    result=convert(source,tmp_path/'output',uf='SP',cnae='620')
    assert result['records']==1
    rows=json.loads((tmp_path/'output'/'empresas-001.json').read_text(encoding='utf-8'))
    assert rows[0]['cnpj']=='00123456000100'
