from dataclasses import dataclass

from src.core.exceptions import ConfigError
from src.core.file_tools import read_yaml


@dataclass
class SystemConfig:
    user_agent: str
    miniapp_version: str
    referer: str
    tenant: str

    @classmethod
    def from_yaml(cls, file_path: str) -> "SystemConfig":
        """从 YAML 文件读取系统配置"""
        try:
            return cls(**read_yaml(file_path))
        except Exception as e:
            raise ConfigError(file_path) from e
