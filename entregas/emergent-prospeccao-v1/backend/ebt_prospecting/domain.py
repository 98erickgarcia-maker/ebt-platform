import hashlib
import json
import re
import unicodedata
from datetime import date, datetime, timezone
from urllib.parse import quote, urlencode, urlparse

EMAIL = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}$")
VARIABLE = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")
VARIABLES = {"company", "first_name", "contact_name", "city", "sender"}


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def text(value, limit=200):
    return str(value or "").strip()[:limit]


def city_key(value):
    return "".join(c for c in unicodedata.normalize("NFKD", text(value)) if not unicodedata.combining(c)).lower()


def normalize_cnpj(value):
    value = re.sub(r"[./\s-]", "", text(value).upper())
    if not re.fullmatch(r"[A-Z0-9]{12}[0-9]{2}", value) or len(set(value)) == 1:
        raise ValueError("CNPJ inválido; informe os 14 caracteres e os dígitos verificadores.")
    base = value[:12]
    for weights in ([5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]):
        remainder = sum((ord(char) - 48) * weight for char, weight in zip(base, weights)) % 11
        base += str(0 if remainder < 2 else 11 - remainder)
    if base != value:
        raise ValueError("Dígitos verificadores do CNPJ inválidos.")
    return value


def safe_url(value, linkedin=False):
    value = text(value, 500)
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        return ""
    if linkedin and parsed.hostname not in {"linkedin.com", "www.linkedin.com", "br.linkedin.com"}:
        return ""
    return value


def valid_email(value):
    value = text(value, 254).lower()
    return value if EMAIL.fullmatch(value) and ".." not in value else ""


def normalize_company(row, source):
    company = text(row.get("company_name") or row.get("razao_social"))
    if not company:
        raise ValueError("Empresa sem razão social.")
    source_date = date.fromisoformat(source["date"])
    if source_date > date.today() or not safe_url(source.get("url")):
        raise ValueError("Informe a data real e a URL pública da fonte.")
    uf = text(row.get("uf")).upper()
    if uf not in {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}:
        raise ValueError("UF inválida.")
    email = valid_email(row.get("email"))
    phone = re.sub(r"\D", "", text(row.get("phone"), 30))
    if len(phone) in (10, 11):
        phone = "55" + phone
    phone = phone if 12 <= len(phone) <= 15 else ""
    active = str(row.get("status", "")).lower() in {"02", "2", "active", "ativa", "ativo"}
    city = text(row.get("city") or row.get("municipio"))
    reasons = []
    if active:
        reasons.append((35, "Cadastro ativo na fonte"))
    if email:
        reasons.append((30, "E-mail com formato válido; caixa ainda não verificada"))
    if phone:
        reasons.append((10, "Telefone informado na fonte; WhatsApp não confirmado"))
    if city:
        reasons.append((10, "Município e UF disponíveis"))
    website = safe_url(row.get("website"))
    if website:
        reasons.append((5, "Site informado; conteúdo não verificado"))
    return {
        "cnpj": normalize_cnpj(row.get("cnpj")), "company_name": company,
        "trade_name": text(row.get("trade_name")), "city": city, "city_key": city_key(city), "uf": uf,
        "cnae": re.sub(r"\D", "", text(row.get("cnae"), 12)), "company_size": text(row.get("company_size"), 50),
        "email": email, "email_quality": "unverified" if email else "missing", "phone": phone,
        "contact_name": text(row.get("contact_name")), "contact_role": text(row.get("contact_role")),
        "website": website, "linkedin": safe_url(row.get("linkedin"), True), "address": text(row.get("address"), 500),
        "active": active, "score": sum(points for points, _ in reasons), "score_reasons": [reason for _, reason in reasons],
        "source": {"name": text(source.get("name")), "url": source["url"], "date": source_date.isoformat()},
        "observed_at": now(),
    }


def render_template(template, contact, sender):
    name = text(contact.get("contact_name"))
    values = {"company": text(contact.get("company_name")), "contact_name": name or "equipe",
              "first_name": name.split()[0] if name else "equipe", "city": text(contact.get("city")), "sender": text(sender)}
    def render(content):
        def substitute(match):
            key = match.group(1)
            if key not in VARIABLES or not values[key]:
                raise ValueError(f"Variável não preenchida ou desconhecida: {key}")
            return values[key]
        if "{{" in VARIABLE.sub("", content) or "}}" in VARIABLE.sub("", content):
            raise ValueError("Sintaxe de variável inválida.")
        return VARIABLE.sub(substitute, content)
    return {"subject": render(template.get("subject", "")), "body": render(template["body"]), "template_version": template["version"]}


def direct_links(contact, subject="", body=""):
    links = {}
    email = valid_email(contact.get("email"))
    if email:
        links["email"] = f"mailto:{quote(email, safe='@')}?{urlencode({'subject': subject.replace(chr(13), '').replace(chr(10), ''), 'body': body}, quote_via=quote)}"
    phone = re.sub(r"\D", "", str(contact.get("phone", "")))
    if 12 <= len(phone) <= 15:
        links["phone"] = f"tel:+{phone}"
        links["whatsapp"] = f"https://wa.me/{phone}?text={quote(body)}"
    for key in ("website", "linkedin"):
        url = safe_url(contact.get(key), key == "linkedin")
        if url:
            links[key] = url
    links["maps"] = "https://www.google.com/maps/search/?api=1&query=" + quote(" ".join(str(contact.get(k, "")) for k in ("company_name", "city", "uf")))
    return links


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


DEFAULT_TEMPLATES = [
    {"id": "presentation", "name": "Apresentação EBT por e-mail", "channel": "email", "subject": "Organização e automação — {{company}}", "body": "Olá {{first_name}}, tudo bem?\n\nSou {{sender}}, da EBT Enterprise. Apoiamos empresas na organização de contatos, processos e atendimento, com sites, CRM e automações ajustados à rotina.\n\nComo esse trabalho funciona hoje na {{company}}? Podemos marcar uma conversa breve para entender as prioridades?\n\nAtenciosamente,\n{{sender}}\n\nSe preferir não receber novos contatos, responda informando sua preferência."},
    {"id": "followup", "name": "Retorno e responsável", "channel": "email", "subject": "Retorno — {{company}}", "body": "Olá {{first_name}},\n\nRetomo minha apresentação para saber se organizar contatos e automatizar tarefas é uma prioridade para a {{company}}. Se outra pessoa for responsável, poderia indicar o melhor canal?\n\nObrigado,\n{{sender}}\n\nSe não houver interesse em novos contatos, basta me avisar."},
    {"id": "sst", "name": "SST e treinamentos — estilo CASST", "channel": "email", "subject": "Organização de SST — {{company}}", "body": "Olá {{first_name}},\n\nGostaria de entender como a {{company}} organiza treinamentos, documentos e vencimentos de SST. Podemos conversar sobre as demandas atuais e avaliar uma proposta conforme o que vocês precisam?\n\n{{sender}}\n\nCaso prefira não receber novos contatos, responda esta mensagem."},
    {"id": "whatsapp_intro", "name": "WhatsApp — prévia de apresentação", "channel": "whatsapp", "subject": "", "body": "Olá {{first_name}}! Sou {{sender}}, da EBT Enterprise. Podemos conversar sobre a organização de contatos e processos na {{company}}? Se preferir não receber mensagens, me avise."},
]
