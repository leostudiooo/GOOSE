import base64
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


class User(BaseModel):
    token: str
    date_time: datetime
    start_image: str
    finish_image: str
    route: str
    custom_track: str = ""

    @classmethod
    @field_validator("token")
    def validate_token(cls, v: Any):
        splits = v.split(".")
        if len(splits) != 3:
            raise ValueError("无效的token. token 必须包含三个部分，如 'part1.part2.part3'")
        try:
            decoded_token = base64.b64decode(splits[1] + "==")
            params = json.loads(decoded_token)
        except Exception as e:
            raise ValueError("无效的token. 此token无法被解码") from e
        if "userid" not in params:
            raise ValueError("无效的token. 此token中没有userid字段")
        return v

    @property
    def student_id(self) -> str:
        splits = self.token.split(".")
        decoded_token = base64.b64decode(splits[1] + "==")
        user_id = json.loads(decoded_token)["userid"]

        return user_id
