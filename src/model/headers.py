from pydantic import BaseModel


class Headers(BaseModel):
    """
    HTTP请求头信息模型
    
    包含API请求所需的各种请求头字段。
    """
    user_agent: str  # 用户代理字符串
    miniapp_version: str  # 小程序版本号
    referer: str  # 请求来源URL
    tenant: str  # 租户标识
