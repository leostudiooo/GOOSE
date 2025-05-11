import json
from json import JSONDecodeError
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError
from yaml import YAMLError

from src.infrastructure.exceptions import FileHandlerError, ModelValidationError
from src.infrastructure.file_handler import FileHandler

T = TypeVar("T", bound="BaseModel")


def load_model_from_json(file_path: Path, model_class: type[T]) -> T:
    with FileHandler(file_path) as f:
        try:
            return model_class.model_validate(json.loads(f.read()))
        except JSONDecodeError as e:
            msg = f"解析 JSON 文件 '{file_path}' 失败"
            raise FileHandlerError(Path(file_path), msg) from e
        except ValidationError as e:
            raise ModelValidationError(f"文件 '{file_path}' 验证不通过", e) from e


def dump_model_to_json(file_path: Path, model: BaseModel):
    with FileHandler(file_path, "w") as f:
        try:
            f.write(model.model_dump_json(indent=4))
        except Exception as e:
            msg = f"保存文件 '{file_path}' 失败"
            raise FileHandlerError(Path(file_path), msg) from e


def load_model_from_yaml(file_path: Path, model_class: type[T]) -> T:
    with FileHandler(file_path) as f:
        try:
            return model_class.model_validate(yaml.safe_load(f.read()))
        except YAMLError as e:
            msg = f"解析 YAML 文件 '{file_path}' 失败"
            raise FileHandlerError(Path(file_path), msg) from e
        except ValidationError as e:
            raise ModelValidationError(f"文件 '{file_path}' 验证不通过", e) from e


def dump_model_to_yaml(file_path: Path, model: BaseModel):
    with FileHandler(file_path, "w") as f:
        try:
            f.write(yaml.safe_dump(model.model_dump()))
        except Exception as e:
            msg = f"保存文件 '{file_path}' 失败"
            raise FileHandlerError(Path(file_path), msg) from e
