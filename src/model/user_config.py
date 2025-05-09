import base64
from datetime import datetime
import json

from pydantic import BaseModel, computed_field

from src.core.exceptions import ConfigError
from src.core.file_tools import read_yaml


class UserConfig(BaseModel):
    token: str
    date_time: datetime
    duration: int
    start_image: str
    finish_image: str
    route: str
    custom_track: str

    @classmethod
    def from_yaml(cls, file_path: str) -> "UserConfig":
        """从 YAML 文件读取用户配置"""
        try:
            return cls.model_validate(read_yaml(file_path))
        except Exception as e:
            raise ConfigError(file_path) from e

    @computed_field
    @property
    def student_id(self) -> str:
        splits = self.token.split(".")
        if len(splits) != 3:
            raise ValueError("无效的token")
        try:
            decoded_token = base64.b64decode(splits[1] + "==")
            user_id = json.loads(decoded_token)["userid"]
        except Exception as e:
            raise ValueError("无效的token") from e

        return user_id
