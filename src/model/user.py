import base64
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.infrastructure.constants import TOKEN_PARTS_COUNT, TOKEN_USERID_FIELD
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
    custom_track: CustomTrack = Field(default_factory=CustomTrack)

    def decode_token(self) -> dict[str, Any]:
        """
        该方法会检查 token 是否由点分隔的三个部分组成, 对来自Base64的第二部分 (有效载荷) 进行解码, 并验证其是否包含必填的 userid 字段.
        解码失败则会抛出 InvalidTokenError 异常.
        """

        splits = self.token.split(".")
        if len(splits) != TOKEN_PARTS_COUNT:
            msg = f"token 必须包含 {TOKEN_PARTS_COUNT} 个部分, 形如 'part1.part2.part3'"
            raise InvalidTokenError(self.token, msg)
        try:
            decoded_token = base64.urlsafe_b64decode(
                splits[1] + "=" * (-len(splits[1]) % 4)
            )  # 处理 base64 URL 编码
            params = json.loads(decoded_token)
        except Exception as e:
            raise InvalidTokenError(self.token, "此token无法被解码") from e
        if TOKEN_USERID_FIELD not in params:
            raise InvalidTokenError(self.token, f"此token中没有{TOKEN_USERID_FIELD}字段")

        return params

    @property
    def student_id(self) -> str:
        params = self.decode_token()
        user_id: str = params[TOKEN_USERID_FIELD]

        return user_id

    @property
    def custom_track_path(self) -> str:
        """获取自定义轨迹文件路径, 如果未启用则返回空字符串"""
        return self.custom_track.file_path if self.custom_track.enable else ""

    @classmethod
    def get_default(cls) -> "User":
        return cls(
            token="your.token.here",
            date_time=datetime(2025, 3, 19, 21, 1, 50),
            start_image="path/to/start/image.jpg",
            finish_image="path/to/finish/image.jpg",
            route="梅园田径场",
            custom_track=CustomTrack(enable=False, file_path="path/to/custom/track.yaml"),
        )
