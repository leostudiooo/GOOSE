import base64
import json
from datetime import datetime
from typing import Any, Union

from pydantic import BaseModel, Field, field_validator

from src.infrastructure.exceptions import InvalidTokenError


class CustomTrack(BaseModel):
    enable: bool = False
    file_path: str = ""


class User(BaseModel):
    token: str
    date_time: datetime
    start_image: str
    finish_image: str
    route: str
    custom_track: Union[str, CustomTrack] = Field(default_factory=CustomTrack)

    @field_validator("custom_track", mode="before")
    @classmethod
    def validate_custom_track(cls, v: Any):
        # 处理字符串类型的custom_track, 转换为CustomTrack对象
        if isinstance(v, str):
            if v:
                return CustomTrack(enable=True, file_path=v)
            return CustomTrack()
        return v

    def validate_token(self) -> None:
        """
        验证 token 的格式和内容。
        
        该方法检查 token 是否由点分隔的三个部分组成, 
        对来自Base64的第二部分 (有效载荷) 进行解码, 并验证其是否包含必填的“userid”字段。

        :raises
        InvalidTokenError：如果 token 没有三个部分、无法解码, 或者不包含“userid”字段。
        """

        splits = self.token.split(".")
        if len(splits) != 3:
            msg = f"token 必须包含三个部分, 形如 'part1.part2.part3'"
            raise InvalidTokenError(self.token, msg)
        try:
            decoded_token = base64.b64decode(splits[1].replace('-', '+').replace('_', '/') + "==") # 处理 base64 URL 编码
            params = json.loads(decoded_token)
        except Exception as e:
            raise InvalidTokenError(self.token, "此token无法被解码") from e
        if "userid" not in params:
            raise InvalidTokenError(self.token, "此token中没有userid字段")

    @property
    def student_id(self) -> str:
        self.validate_token()
        splits = self.token.split(".")
        decoded_token = base64.b64decode(splits[1] + "==")
        user_id = json.loads(decoded_token)["userid"]

        return user_id

    @property
    def custom_track_path(self) -> str:
        """获取自定义轨迹文件路径, 如果未启用则返回空字符串"""
        if isinstance(self.custom_track, str):
            # 向下兼容旧配置
            return self.custom_track
        return self.custom_track.file_path if self.custom_track.enable else ""
