import json
from json import JSONDecodeError
from pathlib import Path
from typing import Generic, TypeVar

import yaml
from pydantic import ValidationError, BaseModel
from yaml import YAMLError

from src.infrastructure.exceptions import ModelStorageError, ModelValidationError

T = TypeVar("T", bound=BaseModel)


class YAMLModelStorage(Generic[T]):
    def __init__(self, file_dir: Path, model_class: type[T]):
        self._file_dir = file_dir
        self._model_class = model_class

    def load(self, name: str) -> T:
        file_path = self._file_dir / f"{name}.yaml"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f.read())
            return self._model_class.model_validate(data)
        except OSError as e:
            raise ModelStorageError(file_path, "读取文件内容失败") from e
        except YAMLError as e:
            raise ModelStorageError(file_path, "YAML解析失败") from e
        except ValidationError as e:
            raise ModelValidationError(file_path, "数据验证不通过", e) from e

    def save(self, name: str, model: T) -> None:
        file_path = self._file_dir / f"{name}.yaml"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(yaml.safe_dump(model.model_dump(), allow_unicode=True))
        except OSError as e:
            raise ModelStorageError(file_path, "保存数据模型失败") from e

    def with_file_dir(self, file_dir: Path) -> "YAMLModelStorage[T]":
        return self.__class__(file_dir, self._model_class)


class JSONModelStorage(Generic[T]):
    def __init__(self, file_dir: Path, model_class: type[T]):
        self._file_dir = file_dir
        self._model_class = model_class

    def load(self, name: str) -> T:
        file_path = self._file_dir / f"{name}.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self._model_class.model_validate(data)
        except OSError as e:
            raise ModelStorageError(file_path, "读取文件内容失败") from e
        except JSONDecodeError as e:
            raise ModelStorageError(file_path, "JSON解析失败") from e
        except ValidationError as e:
            raise ModelValidationError(file_path, "数据验证不通过", e) from e

    def save(self, name: str, model: T) -> None:
        file_path = self._file_dir / f"{name}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(model.model_dump(), f, ensure_ascii=False, indent=2)  # JSON序列化
        except OSError as e:
            raise ModelStorageError(file_path, "保存数据模型失败") from e

    def with_file_dir(self, file_dir: Path) -> "JSONModelStorage[T]":
        return self.__class__(file_dir, self._model_class)
