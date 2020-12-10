import pandas as pd
import pytest

from great_expectations.execution_engine import SqlAlchemyExecutionEngine
from great_expectations.validator.validator import Validator

try:
    import sqlalchemy
except ImportError:
    sqlalchemy = None

from great_expectations.execution_engine.sqlalchemy_batch_data import (
    SqlAlchemyBatchData,
)


def test_instantiation_with_table_name(sqlite_view_engine):
    engine = SqlAlchemyExecutionEngine(engine=sqlite_view_engine)
    batch_data = SqlAlchemyBatchData(execution_engine=engine, table_name="test_table",)

    # This is a very hacky type check.
    # A better way would be to figure out the proper parent class for dialects within SQLAlchemy
    assert (
        str(type(batch_data.sql_engine_dialect))[:28] == "<class 'sqlalchemy.dialects."
    )

    assert isinstance(batch_data.selectable, sqlalchemy.Table)

    assert type(batch_data.record_set_name) == str
    assert batch_data.record_set_name == "great_expectations_sub_selection"

    assert batch_data.use_quoted_name == False


def test_head(sqlite_view_engine):
    # Create a larger table so that we can downsample meaningfully
    df = pd.DataFrame({"a": range(100)})
    df.to_sql("test_table_2", con=sqlite_view_engine)

    engine = SqlAlchemyExecutionEngine(engine=sqlite_view_engine)
    batch_data = SqlAlchemyBatchData(
        execution_engine=engine, table_name="test_table_2",
    )
    engine.load_batch_data("__", batch_data)
    validator = Validator(execution_engine=engine)
    df = validator.head()
    assert df.shape == (5, 2)

    assert validator.head(fetch_all=True).shape == (100, 2)
    assert validator.head(n_rows=20).shape == (20, 2)
    assert validator.head(n_rows=20, fetch_all=True).shape == (100, 2)
