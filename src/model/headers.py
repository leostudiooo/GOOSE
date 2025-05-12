from pydantic import BaseModel, HttpUrl


class Headers(BaseModel):
    user_agent: str
    miniapp_version: str
    referer: HttpUrl
    tenant: str
