import json
import logging
import os
from typing import BinaryIO

import yaml

logger = logging.getLogger(__name__)


def validate_file_path(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到名为 '{file_path}' 的文件")

    if not os.path.isfile(file_path):
        raise ValueError(f"路径 '{file_path}' 不是一个常规文件")


def read_json(file_path: str, encoding: str = "utf-8") -> str:
    validate_file_path(file_path)
    try:
        with open(file_path, "r", encoding=encoding) as file:
            return file.read()
    except Exception as e:
        raise ValueError(f"文件 '{file_path}' 读取失败: {e}") from e


def validate_jpg(file_path: str):
    validate_file_path(file_path)
    if not (file_path.endswith(".jpg") or file_path.endswith(".jpeg")):
        raise ValueError(f"文件 '{file_path}' 不是一个有效的 JPG 文件")


def read_yaml(file_path: str, encoding: str = "utf-8") -> dict:
    validate_file_path(file_path)
    try:
        with open(file_path, "r", encoding=encoding) as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise ValueError(f"读取 YAML 文件 '{file_path}' 失败: {e}") from e
