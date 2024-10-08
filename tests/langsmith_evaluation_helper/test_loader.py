# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar
from unittest import mock

import pytest
from langsmith.schemas import Example

from tests.factory import example_factory

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
    async def async_func() -> None:
        pass

    def sync_func() -> None:
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
) -> None:
    module_path = create_sample_module(tmp_path=tmp_path, module_name=sample_module_name)

    if expected_exception_type:
        with pytest.raises(expected_exception_type):
            load_function(str(module_path), function_name)
    else:
        loaded_function = load_function(str(module_path), function_name)
        assert inspect.isfunction(loaded_function)
        assert isinstance(loaded_function, expected_output_type)


response_examples: list[Example] = [
    example_factory(
        inputs={"name": "Example1"}, outputs={"output": "example output 1"}, metadata={"dataset_split": ["base"]}
    ),
    example_factory(
        inputs={"name": "Example2"}, outputs={"output": "example output 2"}, metadata={"dataset_split": ["test"]}
    ),
    example_factory(
        inputs={"name": "Example3"}, outputs={"output": "example output 3"}, metadata={"dataset_split": ["base"]}
    ),
    example_factory(
        inputs={"name": "Example4"}, outputs={"output": "example output 4"}, metadata={"dataset_split": ["other"]}
    ),
]


@pytest.mark.parametrize("config_content", Configurations.get_all_configs())
@mock.patch("langsmith_evaluation_helper.loader.Client")
def test_load_dataset(
    mock_client: mock.MagicMock,
    config_content: str,
    create_temp_config_file: Callable[[str], Path],
) -> None:
    mock_client.return_value = MockClient(response_examples=response_examples)
    config_file_path = create_temp_config_file(config_content)
    config_file = load_config(str(config_file_path))

    test_info = config_file["tests"]
    split_string = test_info.get("split", None)
    limit = test_info.get("limit", None)
    dataset_output, experiment_prefix, _, metadata_keys = load_dataset(config_file)

    # Testing for no-split, no-limit
    expected_dataset_name = test_info["dataset_name"]
    expected_experiment_prefix = test_info["experiment_prefix"]
    if split_string is None and limit is None and len(metadata_keys) == 0:
        assert dataset_output == expected_dataset_name
        assert experiment_prefix == expected_experiment_prefix

    if split_string is None and limit is None and len(metadata_keys) > 0:
        assert dataset_output == response_examples
        assert experiment_prefix == expected_experiment_prefix

    mocked_examples = response_examples
    # Testing for split, no-limit
    if split_string is not None and limit is None:
        expected_examples = [
            example
            for example in mocked_examples
            if example.metadata is not None
            and any(split in example.metadata["dataset_split"] for split in split_string.split(" "))
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
            and any(split in example.metadata["dataset_split"] for split in split_string.split(" "))
        ][:limit]
        assert dataset_output == expected_examples
        assert experiment_prefix == expected_experiment_prefix


@pytest.mark.asyncio
@pytest.mark.parametrize("config_content", Configurations.get_all_configs())
@mock.patch("langsmith_evaluation_helper.loader.load_dataset")
@mock.patch("langsmith_evaluation_helper.loader.load_evaluators")
@mock.patch("langsmith_evaluation_helper.loader.run_evaluate", new_callable=mock.AsyncMock)
@mock.patch("langsmith_evaluation_helper.loader.LANGCHAIN_TENANT_ID", new="dummy_tenant_id")
async def test_main(
    mock_run_evaluate: mock.MagicMock,
    mock_load_evaluators: mock.MagicMock,
    mock_load_dataset: mock.MagicMock,
    config_content: str,
    create_temp_config_file: Callable[[str], Path],
) -> None:
    # Mocking values
    mock_load_dataset.return_value = (
        "dataset_name",
        "experiment_prefix",
        "num_repititions",
        [],
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
