# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest import mock
from uuid import uuid4

import pytest
from langsmith.evaluation import (
    EvaluationResult,
    EvaluationResults,
)
from langsmith.schemas import Example, Run

from .config_input import Configurations
from langsmith_evaluation_helper.builtin_evaluators import (
    create_length_evaluator,
    create_llm_judge_evaluator,
    create_similar_evaluator,
    generate_builtin_evaluator_functions,
)
from langsmith_evaluation_helper.loader import (
    load_config,
)


@pytest.mark.parametrize("config", Configurations.get_all_configs())
def test_generate_builtin_evaluator_functions(config: str, create_temp_config_file: Callable[[str], Path]) -> None:
    config_file_path = create_temp_config_file(config)
    config_file = load_config(str(config_file_path))
    builtin_evaluators_config = config_file["tests"].get("assert", [])
    builtin_evaluators = generate_builtin_evaluator_functions(builtin_evaluators_config)

    # Test : If builtin_evaluators_config is None, Builtin_evaluators should be none.
    if not builtin_evaluators_config:
        assert builtin_evaluators == []
    else:  # Checking if length of both the lists are same
        assert len(builtin_evaluators_config) == len(builtin_evaluators)

        # Assert if list
        assert isinstance(builtin_evaluators, list)

        # Assert if every item is a callable (Evaluator)
        assert all(callable(eval) for eval in builtin_evaluators)


@pytest.mark.parametrize("config", Configurations.get_config("multiple_asserts"))
def test_specific_evaluator_generation(config: str, create_temp_config_file: Callable[[str], Path]) -> None:
    config_file_path = create_temp_config_file(config)
    config_file = load_config(str(config_file_path))
    builtin_evaluators_config = config_file["tests"].get("assert", [])
    evaluators = generate_builtin_evaluator_functions(builtin_evaluators_config)

    assert evaluators[0].__name__ == "length_evaluator"
    assert evaluators[1].__name__ == "llm_judge_evaluator"
    assert evaluators[2].__name__ == "similar_evaluator"


def run_factory(name: str = "", inputs: dict[str, Any] | None = None, outputs: dict[str, Any] | None = None) -> Run:
    if inputs is None:
        inputs = {}
    if outputs is None:
        outputs = {}

    return Run(
        id=str(uuid4()),
        name=name,
        start_time=datetime.now(),
        run_type="test_type",
        trace_id=str(uuid4()),
        inputs={},
        outputs=outputs,
    )


def example_factory(inputs: dict[str, Any] | None = None, outputs: dict[str, Any] | None = None) -> Example:
    if inputs is None:
        inputs = {}
    if outputs is None:
        outputs = {}

    return Example(
        id=str(uuid4()),
        dataset_id=str(uuid4()),
        created_at=datetime.now(),
        inputs={},
        metadata={},
        modified_at=None,
        outputs=outputs,
        runs=[],
    )


@pytest.mark.parametrize("config", Configurations.get_config("multiple_asserts"))
def test_length_evaluator_logic(config: str, create_temp_config_file: Callable[[str], Path]) -> None:
    config_file_path = create_temp_config_file(config)
    config_file = load_config(str(config_file_path))
    builtin_evaluators_config = config_file["tests"].get("assert", [])

    evaluator = create_length_evaluator(builtin_evaluators_config[0])

    run1 = run_factory(name="test_run_2", outputs={"output": "a" * 200})

    example = example_factory(inputs={"None": None})

    result = evaluator(run1, example)

    assert result == {"key": "length", "score": True}

    run2 = run_factory(name="test_run_2", outputs={"output": "a" * 201})
    result = evaluator(run2, example)
    assert result == {"key": "length", "score": False}


@pytest.mark.parametrize("config", Configurations.get_config("multiple_asserts"))
@mock.patch("langsmith_evaluation_helper.llm.model.ChatModel.invoke", return_value="0.9")
def test_llm_judge_evaluator_logic(
    mock_invoke: mock.MagicMock, config: str, create_temp_config_file: Callable[[str], Path]
) -> None:
    config_file_path = create_temp_config_file(config)
    config_file = load_config(str(config_file_path))
    builtin_evaluators_config = config_file["tests"].get("assert", [])

    # Choosing builtin_evaluators_config[1] , 1 index based on the input config file.
    evaluator = create_llm_judge_evaluator(builtin_evaluators_config[1])
    run1 = run_factory(name="test_run_2", outputs={"output": "I hate you"})
    example = example_factory(inputs={"None": None})

    result = evaluator(run1, example)

    assert result == {"key": "llm-judge", "score": 0.9}
    mock_invoke.assert_called_once()


@pytest.mark.parametrize("config", Configurations.get_config("multiple_asserts"))
def test_similar_evaluator(config: str, create_temp_config_file: Callable[[str], Path]) -> None:
    config_file_path = create_temp_config_file(config)
    config_file = load_config(str(config_file_path))
    config_file["tests"].get("assert", [])

    evaluator = create_similar_evaluator()
    run = run_factory(name="test_run_2", outputs={"output": "I hate you"})
    example = example_factory(inputs={"None": None}, outputs={"output": "I hate you"})

    result = evaluator(run, example)

    assert isinstance(result, EvaluationResult | EvaluationResults)  # type: ignore
