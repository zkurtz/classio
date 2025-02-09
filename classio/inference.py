"""Inference of IO methods based on class annotations."""

import importlib
from types import ModuleType
from typing import Any, Dict


def _is_dict_annotation(annotation: Any) -> bool:
    """Checks if a type annotation is a dictionary.

    Args:
        annotation: The type annotation to check.
    """
    if hasattr(annotation, "__origin__"):
        return annotation.__origin__ in {dict, Dict}
    return False


def _is_pydantic_annotation(annotation: Any) -> bool:
    """Guesses whether an annotation refers to a pydantic model.

    Args:
        annotation: The type annotation to check.
    """
    return hasattr(annotation, "model_validate_json")


def _is_mashumaro_annotation(annotation: Any) -> bool:
    """Guesses whether an annotation refers to a mashumaro model.

    Args:
        annotation: The type annotation to check.
    """
    return "_DataClassDictMixin__mashumaro_builder_params" in dir(annotation)


def _is_mashumaro_yaml_annotation(annotation: Any) -> bool:
    """Guesses whether an annotation refers to a mashumaro model with a `to_yaml` method.

    Args:
        annotation: The type annotation to check.
    """
    return _is_mashumaro_annotation(annotation) and hasattr(annotation, "to_yaml")


def _is_mashumaro_json_annotation(annotation: Any) -> bool:
    """Guesses whether an annotation refers to a mashumaro model with a `to_json` method.

    Args:
        annotation: The type annotation to check.
    """
    return _is_mashumaro_annotation(annotation) and hasattr(annotation, "to_json")


def load_requires_model(annotation: Any) -> bool:
    """Checks if load method on the IO module implied by annotation requires the data model/class to be passed.

    Args:
        annotation: The type annotation to check.
    """
    return (
        _is_pydantic_annotation(annotation)
        or _is_mashumaro_yaml_annotation(annotation)
        or _is_mashumaro_json_annotation(annotation)
    )


def infer_io_module(name: str, *, annotation: Any) -> ModuleType:
    """Deduce the IO module to use based on a type annotation.

    Args:
        name: The name of the attribute. Provided only for the error message that's raised in case the type can't be
            deduced from the annotation.
        annotation: The type annotation of the attribute.

    Returns:
        An IO module, having methods `save` and `load`.
    """
    if annotation is str:
        return importlib.import_module("dummio.text")
    elif _is_dict_annotation(annotation):
        return importlib.import_module("dummio.json")
    elif annotation.__module__ == "pandas.core.frame":
        return importlib.import_module("dummio.pandas.df_parquet")
    elif _is_pydantic_annotation(annotation):
        return importlib.import_module("dummio.pydantic")
    elif annotation.__name__ == "ModelProto" and annotation.__module__ == "onnx.onnx_ml_pb2":
        return importlib.import_module("dummio.onnx")
    elif _is_mashumaro_yaml_annotation(annotation):
        return importlib.import_module("dummio.mashumaro.yaml")
    elif _is_mashumaro_json_annotation(annotation):
        return importlib.import_module("dummio.mashumaro.json")
    raise ValueError(f"No IO module provided or inferred for {name}: {annotation}")
