import pytest
from ebt_prospecting.domain import normalize_company, render_template, direct_links

SOURCE = {"url": "https://example.com/catalog", "date": "2026-10-01", "name": "Base sintética"}
ROW = {"cnpj": "11.222.333/0001-81", "company_name": "Empresa Exemplo", "city": "São Paulo", "uf": "SP", "cnae": "6201501", "email": "comercial@example.com", "phone": "5511999999999", "status": "02"}


def test_numeric_and_alphanumeric_cnpj_survive_import():
    assert normalize_company(ROW, SOURCE)["cnpj"] == "11222333000181"
    alpha = normalize_company({**ROW, "cnpj": "12.ABC.345/01DE-35"}, SOURCE)
    assert alpha["cnpj"] == "12ABC34501DE35"
    assert alpha["city_key"] == "sao paulo"


@pytest.mark.parametrize("cnpj", ["00000000000000", "11222333000182", "ABCDEFGHIJKLMN", "", "11222333000181<script>"])
def test_invalid_identifiers_are_rejected(cnpj):
    with pytest.raises(ValueError):
        normalize_company({**ROW, "cnpj": cnpj}, SOURCE)


def test_public_email_is_not_claimed_verified_or_consented():
    row = normalize_company(ROW, SOURCE)
    assert row["email_quality"] == "unverified"
    assert row["score"] == 85
    assert row["score_reasons"]
    assert row["source"]["date"] == "2026-10-01"
    assert not row.get("consent", False)


def test_templates_resolve_values_without_recursive_expansion():
    tpl = {"subject": "Olá {{company}}", "body": "{{first_name}}, {{sender}} atende {{company}}.", "version": 1}
    out = render_template(tpl, {"company_name": "Empresa X", "contact_name": "Ana Maria"}, "Erick")
    assert out == {"subject": "Olá Empresa X", "body": "Ana, Erick atende Empresa X.", "template_version": 1}
    out = render_template(tpl, {"company_name": "{{sender}}", "contact_name": "Ana"}, "Erick")
    assert out["subject"] == "Olá {{sender}}"


def test_unknown_variables_and_missing_sender_are_blocked():
    with pytest.raises(ValueError):
        render_template({"subject": "{{password}}", "body": "teste", "version": 1}, ROW, "Erick")
    with pytest.raises(ValueError):
        render_template({"subject": "Teste", "body": "{{sender}}", "version": 1}, ROW, "")


def test_links_encode_message_and_never_inject_headers_or_javascript():
    links = direct_links({**ROW, "company_name": "A&B", "website": "javascript:alert(1)", "linkedin": "https://linkedin.com/company/example"}, "Olá & bom dia", "texto? & teste")
    assert "subject=Ol%C3%A1%20%26%20bom%20dia" in links["email"]
    assert links["whatsapp"].startswith("https://wa.me/5511999999999?text=")
    assert "website" not in links
    assert "email" not in direct_links({"email": "a@example.com\r\nBcc: b@example.com"})
