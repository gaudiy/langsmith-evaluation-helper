# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any
from unittest.mock import patch

import pytest

from langsmith_evaluation_helper.load_run_function import (
    load_prompt_function,
    load_prompt_template,
    load_run_function,
)


def create_mock_config(custom_run: bool = False) -> dict[str, Any]:
    config = {}
    if not custom_run:
        config["prompt"] = {
            "name": "mock_prompt.py",
            "entry_function": "mock_entry_function",
        }
    if custom_run:
        config["custom_run"] = {
            "file_path": "mock_custom_run.py",
            "entry_function": "mock_custom_entry_function",
        }
    return config


mock_provider = {"id": "mock_provider", "config": {"temperature": 0.7}}


@pytest.mark.parametrize(
    "config_type,expected_function",
    [
        ("prompt", load_prompt_template),
        ("custom_run", load_prompt_function),
    ],
)
def test_load_run_function(config_type: str) -> None:
    mock_config = create_mock_config(
        custom_run=(config_type == "custom_run"),
    )
    if config_type == "none":
        mock_config = {}

    with (
        patch("langsmith_evaluation_helper.load_run_function.load_prompt_template") as mock_load_template,
        patch("langsmith_evaluation_helper.load_run_function.load_prompt_function") as mock_load_function,
    ):
        mock_load_template.return_value = lambda x: "template_result"
        mock_load_function.return_value = lambda x: "function_result"

        result = load_run_function("/mock/path/config.yaml", mock_config, mock_provider)

        if config_type == "none":
            assert result is None
        else:
            assert callable(result)
            if config_type == "prompt":
                mock_load_template.assert_called_once_with("/mock/path/config.yaml", mock_config, mock_provider)
                assert result({"input": "test"}) == "template_result"
            elif config_type == "custom_run":
                assert result({"input": "test"}) == "function_result"


@pytest.mark.asyncio
async def test_load_run_function_async() -> None:
    mock_config = create_mock_config(custom_run=True)

    async def mock_async_function(inputs: dict[Any, Any]) -> Any:
        return inputs

    with patch("langsmith_evaluation_helper.load_run_function.load_prompt_function") as mock_load_func:
        mock_load_func.return_value = mock_async_function

        result = load_run_function("/mock/path/config.yaml", mock_config, mock_provider)

        assert callable(result)
        assert isinstance(await result({"test": "input"}), dict)
        assert await result({"test": "input"}) == {"test": "input"}


def test_load_run_function_error() -> None:
    mock_config = {
        "prompt": {"name": "mock_prompt.py", "entry_function": "mock_entry_function"},
        "custom_run": {
            "name": "mock_custom_run.py",
            "entry_function": "mock_custom_entry_function",
        },
    }

    with pytest.raises(ValueError, match="prompt and custom_run cannot be specified simultaneously"):
        load_run_function("/mock/path/config.yaml", mock_config, mock_provider)


if __name__ == "__main__":
    pytest.main()
