import base64
import json
from datetime import datetime
from typing import Any, Union

from pydantic import BaseModel, Field, field_validator


class CustomTrack(BaseModel):
    enable: bool = False
    file_path: str = ""


class User(BaseModel):
    token: str
    date_time: datetime
    start_image: str
    finish_image: str
    route: str
    custom_track: Union[str, CustomTrack] = Field(default_factory=lambda: CustomTrack())

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

    @property
    def custom_track_path(self) -> str:
        """获取自定义轨迹文件路径，如果未启用则返回空字符串"""
        if isinstance(self.custom_track, str):
            # 向下兼容旧配置
            return self.custom_track
        return self.custom_track.file if self.custom_track.enable else ""