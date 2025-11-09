import json
from json import JSONDecodeError
from pathlib import Path
from typing import Generic, TypeVar

import yaml
from pydantic import BaseModel, ValidationError
from yaml import YAMLError

from src.infrastructure.exceptions import ModelStorageError, ModelValidationError

T = TypeVar("T", bound=BaseModel)


class YAMLModelStorage(Generic[T]):
    def __init__(self, file_dir: Path, model_class: type[T]):
        self._file_dir = file_dir
        self._model_class = model_class

    def load(self, name: str) -> T:
        json_path = self._file_dir / f"{name}.json"
        yaml_path = self._file_dir / f"{name}.yaml"

        if json_path.exists():
            file_path = json_path
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                return self._model_class.model_validate(data)
            except OSError as e:
                msg = f"从文件 '{file_path}' 中加载数据模型失败"
                raise ModelStorageError(file_path, msg) from e
            except JSONDecodeError as e:
                msg = f"从 JSON 文件 '{file_path}' 中加载数据模型失败"
                raise ModelStorageError(file_path, msg) from e
            except ValidationError as e:
                raise ModelValidationError(f"文件 '{file_path}' 验证不通过", e) from e
        else:
            file_path = yaml_path
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = yaml.safe_load(f.read())
                return self._model_class.model_validate(data)
            except OSError as e:
                msg = f"从文件 '{file_path}' 中加载数据模型失败"
                raise ModelStorageError(file_path, msg) from e
            except YAMLError as e:
                msg = f"从 YAML 文件 '{file_path}' 中加载数据模型失败"
                raise ModelStorageError(file_path, msg) from e
            except ValidationError as e:
                raise ModelValidationError(f"文件 '{file_path}' 验证不通过", e) from e

    def save(self, name: str, model: T) -> None:
        file_path = self._file_dir / f"{name}.yaml"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml.safe_dump(model.model_dump(), allow_unicode=True))
        except OSError as e:
            msg = f"保存数据模型到 '{file_path}' 失败"
            raise ModelStorageError(file_path, msg) from e

    def with_file_dir(self, file_dir: Path) -> "YAMLModelStorage[T]":
        return YAMLModelStorage(file_dir, self._model_class)
