"""Testing the classio.declario class decorator."""

from dataclasses import dataclass
import pandas as pd
from classio import declario
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4, UUID
import pydantic
import warnings
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

with warnings.catch_warnings():
    # trying to ignore this exact warning: "DeprecationWarning: datetime.datetime.utcfromtimestamp() is deprecated"
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import onnx
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType


class Metadata(pydantic.BaseModel):
    """ML model metadata."""

    id: UUID
    rmse: float
    trained_at: datetime


@declario()
@dataclass
class ModelPackage:
    """A trained model artifact."""

    documentation: str
    metadata: Metadata
    config: dict[str, int | float]
    train_df: pd.DataFrame
    model: onnx.ModelProto


def build_model() -> ModelPackage:
    """Build a model package."""
    iris = load_iris()
    clr = LogisticRegression(solver="saga", max_iter=10000)
    x_matrix = iris.data  # pyright: ignore[reportAttributeAccessIssue]
    y_vector = iris.target  # pyright: ignore[reportAttributeAccessIssue]
    feature_names = iris.feature_names  # pyright: ignore[reportAttributeAccessIssue]
    clr.fit(x_matrix, y_vector)
    train_df = pd.DataFrame(x_matrix, columns=feature_names)
    train_df["target"] = y_vector
    initial_type = [("float_input", FloatTensorType([None, 4]))]
    onx = convert_sklearn(clr, initial_types=initial_type)
    return ModelPackage(
        documentation="Iris data logistic regression.",
        metadata=Metadata(
            id=uuid4(),
            rmse=0.13,
            trained_at=datetime.now(tz=timezone.utc),
        ),
        config=dict(lr=0.01, num_trees=100),
        train_df=train_df,
        model=onx,
    )


def test_ml_example(tmp_path: Path) -> None:
    """Do IO with a ML model class including pydantic metadata and onnx model format."""
    model = build_model()
    filepath = tmp_path / "test_model"
    model.save(filepath)
    model2 = ModelPackage.load(filepath)

    assert id(model) != id(model2), "Although data2 should equal data, they should not be the same object."
    assert model.metadata == model2.metadata
    assert model.config == model2.config
    assert model.documentation == model2.documentation
    assert model.model == model2.model
    pd.testing.assert_frame_equal(model.train_df, model2.train_df)
