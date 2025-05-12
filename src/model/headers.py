from pydantic import BaseModel


class Headers(BaseModel):
    user_agent: str
    miniapp_version: str
    referer: str
    tenant: str
