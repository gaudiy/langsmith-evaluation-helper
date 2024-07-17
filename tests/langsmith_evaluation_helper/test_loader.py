# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

import datetime
import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar
from unittest import mock
from uuid import UUID

import pytest
from langsmith.schemas import Example

from .config_input import Configurations
from .langsmith_mock import MockClient
from langsmith_evaluation_helper.loader import (
    is_async_function,
    load_config,
    load_dataset,
    load_function,
    main,
)

E = TypeVar("E", bound=BaseException)


# Testing is_async_function
def test_is_async_function() -> None:
    async def async_func():
        pass

    def sync_func():
        pass

    assert is_async_function(async_func) is True
    assert is_async_function(sync_func) is False


sample_module_content = """
def example_prompt_function1():
    return "sample prompt1"

def example_prompt_function2():
    return "sample prompt2"
"""


@pytest.fixture
def sample_module_name() -> str:
    return "example_prompt.py"


def create_sample_module(tmp_path: Path, module_name: str) -> Path:
    module_path = tmp_path / module_name
    module_path.write_text(sample_module_content)
    return module_path


@pytest.mark.parametrize(
    "function_name, expected_output_type, expected_exception_type",
    [
        ("example_prompt_function1", Callable, None),
        ("example_prompt_function2", Callable, None),
        ("non_existent_function", None, AttributeError),
    ],
)
def test_load_function_isfunction(
    tmp_path: Path,
    sample_module_name: str,
    function_name: str,
    expected_output_type: Any,
    expected_exception_type: type[E] | tuple[type[E], ...],
):
    module_path = create_sample_module(
        tmp_path=tmp_path, module_name=sample_module_name
    )

    if expected_exception_type:
        with pytest.raises(expected_exception_type):
            load_function(str(module_path), function_name)
    else:
        loaded_function = load_function(str(module_path), function_name)
        assert inspect.isfunction(loaded_function)
        assert isinstance(loaded_function, expected_output_type)


response_examples: list[Example] = [
    Example(
        dataset_id=UUID("a01b4fbe-2fd5-4fb5-ba2f-75110cfabe6b"),
        inputs={"name": "Example1"},
        outputs={"output": "example output 1"},
        metadata={"dataset_split": ["base"]},
        id=UUID("ef056508-7e6f-44b8-84d7-2a1962d06bd7"),
        created_at=datetime.datetime(
            2024, 5, 17, 5, 35, 51, 352854, tzinfo=datetime.UTC
        ),
        modified_at=datetime.datetime(
            2024, 6, 11, 5, 19, 22, 448182, tzinfo=datetime.UTC
        ),
        runs=[],
        source_run_id=None,
    ),
    Example(
        dataset_id=UUID("a01b4fbe-2fd5-4fb5-ba2f-75110cfabe6b"),
        inputs={"name": "Example2"},
        outputs={"output": "example output 2"},
        metadata={"dataset_split": ["test"]},
        id=UUID("ef056508-7e6f-44b8-84d7-2a1962d06bd7"),
        created_at=datetime.datetime(
            2024, 5, 17, 5, 35, 51, 352854, tzinfo=datetime.UTC
        ),
        modified_at=datetime.datetime(
            2024, 6, 11, 5, 19, 22, 448182, tzinfo=datetime.UTC
        ),
        runs=[],
        source_run_id=None,
    ),
    Example(
        dataset_id=UUID("a01b4fbe-2fd5-4fb5-ba2f-75110cfabe6b"),
        inputs={"name": "Example3"},
        outputs={"output": "example output 3"},
        metadata={"dataset_split": ["base"]},
        id=UUID("ef056508-7e6f-44b8-84d7-2a1962d06bd7"),
        created_at=datetime.datetime(
            2024, 5, 17, 5, 35, 51, 352854, tzinfo=datetime.UTC
        ),
        modified_at=datetime.datetime(
            2024, 6, 11, 5, 19, 22, 448182, tzinfo=datetime.UTC
        ),
        runs=[],
        source_run_id=None,
    ),
    Example(
        dataset_id=UUID("a01b4fbe-2fd5-4fb5-ba2f-75110cfabe6b"),
        inputs={"name": "Example4"},
        outputs={"output": "example output 4"},
        metadata={"dataset_split": ["other"]},
        id=UUID("ef056508-7e6f-44b8-84d7-2a1962d06bd7"),
        created_at=datetime.datetime(
            2024, 5, 17, 5, 35, 51, 352854, tzinfo=datetime.UTC
        ),
        modified_at=datetime.datetime(
            2024, 6, 11, 5, 19, 22, 448182, tzinfo=datetime.UTC
        ),
        runs=[],
        source_run_id=None,
    ),
]


@pytest.mark.parametrize("config_content", Configurations.get_all_configs())
@mock.patch("langsmith_evaluation_helper.loader.Client")
def test_load_dataset(
    mock_client,
    config_content,
    create_temp_config_file,
):
    mock_client.return_value = MockClient(response_examples=response_examples)
    config_file_path = create_temp_config_file(config_content=config_content)
    config_file = load_config(str(config_file_path))

    test_info = config_file["tests"]
    split_string = test_info.get("split", None)
    limit = test_info.get("limit", None)
    dataset_output, experiment_prefix, _ = load_dataset(config_file)

    # Testing for no-split, no-limit
    expected_dataset_name = test_info["dataset_name"]
    expected_experiment_prefix = test_info["experiment_prefix"]
    if split_string is None and limit is None:
        assert dataset_output == expected_dataset_name
        assert experiment_prefix == expected_experiment_prefix

    mocked_examples = response_examples
    # Testing for split, no-limit
    if split_string is not None and limit is None:
        expected_examples = [
            example
            for example in mocked_examples
            if example.metadata is not None
            and any(
                split in example.metadata["dataset_split"]
                for split in split_string.split(" ")
            )
        ]
        assert dataset_output == expected_examples
        if expected_experiment_prefix:
            assert experiment_prefix == expected_experiment_prefix
    # Testing for limit, no-split
    if split_string is None and limit is not None:
        expected_examples = mocked_examples[:limit]
        assert dataset_output == expected_examples
        assert experiment_prefix == expected_experiment_prefix

    # Testing for limit, split
    if split_string is not None and limit is not None:
        expected_examples = [
            example
            for example in mocked_examples
            if example.metadata is not None
            and any(
                split in example.metadata["dataset_split"]
                for split in split_string.split(" ")
            )
        ][:limit]
        assert dataset_output == expected_examples
        assert experiment_prefix == expected_experiment_prefix


# TODO: Also make module_name into parameterization later.


@pytest.mark.asyncio
@pytest.mark.parametrize("config_content", Configurations.get_all_configs())
@mock.patch("langsmith_evaluation_helper.loader.load_dataset")
@mock.patch("langsmith_evaluation_helper.loader.load_evaluators")
@mock.patch(
    "langsmith_evaluation_helper.loader.run_evaluate", new_callable=mock.AsyncMock
)
@mock.patch(
    "langsmith_evaluation_helper.loader.LANGCHAIN_TENANT_ID", new="dummy_tenant_id"
)
async def test_main(
    mock_run_evaluate,
    mock_load_evaluators,
    mock_load_dataset,
    config_content,
    create_temp_config_file,
):
    # Mocking values
    mock_load_dataset.return_value = (
        "dataset_name",
        "experiment_prefix",
        "num_repititions",
    )
    mock_load_evaluators.return_value = (["evaluator1"], ["summary_evaluator1"])
    mock_run_evaluate.return_value = ("dataset_id", "experiment_id")

    # Create a temporary config file
    config_file_path = create_temp_config_file(config_content)

    config_file = load_config(str(config_file_path))

    # Run the main function asynchronously
    await main(config_file)

    # Assertions, function to verify calls.
    mock_load_dataset.assert_called_once_with(config_file)
    mock_load_evaluators.assert_called_once_with(config_file)
    # Verify that the async function was awaited exactly the number of providers provided.
    assert mock_run_evaluate.await_count == len(config_file["providers"])
