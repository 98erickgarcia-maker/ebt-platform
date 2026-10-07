from dataclasses import dataclass, field
import os
from urllib.parse import urlparse


@dataclass
class Config:
    owner_email: str
    workspace: str = "ebt-enterprise"
    origins: list[str] = field(default_factory=list)
    monthly_limit: int = 3000
    daily_email_limit: int = 20
    send_enabled: bool = False
    ms_client_id: str = ""
    ms_tenant_id: str = ""
    ms_client_secret: str = ""
    ms_redirect_uri: str = ""
    token_key: str = ""
    outlook_mode: str = "application"
    sender_mailbox: str = ""
    wa_phone_id: str = ""
    wa_token: str = ""
    wa_app_secret: str = ""
    wa_verify_token: str = ""
    wa_version: str = "v23.0"
    wa_send_enabled: bool = False
    wa_max_cost_brl: float = 0
    wa_template_cost_brl: float = 0

    @classmethod
    def from_env(cls):
        return cls(owner_email=os.getenv("OWNER_EMAIL", "").strip().lower(), workspace=os.getenv("EP_WORKSPACE", "ebt-enterprise"), origins=[o.strip().rstrip("/") for o in os.getenv("FRONTEND_URL", "").split(",") if o.strip()], monthly_limit=int(os.getenv("EP_MONTHLY_LIMIT", "3000")), daily_email_limit=int(os.getenv("EP_DAILY_EMAIL_LIMIT", "20")), send_enabled=os.getenv("EP_EMAIL_SEND_ENABLED", "false").lower()=="true", ms_client_id=os.getenv("MS_CLIENT_ID") or os.getenv("AZURE_CLIENT_ID", ""), ms_tenant_id=os.getenv("MS_TENANT_ID") or os.getenv("AZURE_TENANT_ID", ""), ms_client_secret=os.getenv("MS_CLIENT_SECRET") or os.getenv("AZURE_CLIENT_SECRET", ""), ms_redirect_uri=os.getenv("EP_MS_REDIRECT_URI", ""), token_key=os.getenv("EP_TOKEN_KEY", ""), outlook_mode=os.getenv("EP_OUTLOOK_MODE", "application"), sender_mailbox=os.getenv("EP_SENDER_MAILBOX") or os.getenv("SENDER_MAILBOX", ""), wa_phone_id=os.getenv("EP_WA_PHONE_ID", ""), wa_token=os.getenv("EP_WA_TOKEN", ""), wa_app_secret=os.getenv("EP_WA_APP_SECRET", ""), wa_verify_token=os.getenv("EP_WA_VERIFY_TOKEN", ""), wa_version=os.getenv("EP_WA_VERSION", "v23.0"), wa_send_enabled=os.getenv("EP_WA_SEND_ENABLED", "false").lower()=="true", wa_max_cost_brl=float(os.getenv("EP_WA_MAX_COST_BRL", "0")), wa_template_cost_brl=float(os.getenv("EP_WA_TEMPLATE_COST_BRL", "0")))

    def validate(self):
        if not self.owner_email or not self.workspace or not self.origins:
            raise ValueError("Defina OWNER_EMAIL, EP_WORKSPACE e FRONTEND_URL explicitamente.")
        if not 1 <= self.monthly_limit <= 100000 or not 1 <= self.daily_email_limit <= 500:
            raise ValueError("Limites fora da faixa permitida.")
        if self.outlook_mode not in {"application", "delegated"}:
            raise ValueError("EP_OUTLOOK_MODE deve ser application ou delegated.")
        for origin in self.origins:
            u = urlparse(origin)
            if u.scheme != "https" and not (u.scheme == "http" and u.hostname in {"127.0.0.1", "localhost"}):
                raise ValueError("Origem deve usar HTTPS, exceto desenvolvimento local.")
            if u.path or u.query or u.fragment or u.username or not u.hostname:
                raise ValueError("Origem deve conter apenas protocolo e host.")

    @property
    def outlook_configured(self):
        credentials = all([self.ms_client_id, self.ms_tenant_id, self.ms_client_secret])
        return credentials if self.outlook_mode == "application" else credentials and all([self.ms_redirect_uri, self.token_key])
