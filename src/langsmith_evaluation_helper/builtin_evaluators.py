# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from typing import Any, Literal, Optional, TypedDict

from langchain.prompts.prompt import PromptTemplate
from langsmith.evaluation import (
    EvaluationResult,
    EvaluationResults,
    LangChainStringEvaluator,
)
from langsmith.schemas import Example, Run

from langsmith_evaluation_helper.llm.model import ChatModel, ChatModelName


class BuiltinEvaluatorConfig(TypedDict):
    type: Literal["length", "llm-judge", "similar"]
    value: str
    label: Optional[str]  # noqa: UP007
    judge_provider: dict[Any, Any] | None


class EvalResult(TypedDict):
    key: str | None
    score: float


Evaluator = Callable[[Run, Example], EvalResult | EvaluationResult | EvaluationResults]


def create_length_evaluator(evaluator_config: BuiltinEvaluatorConfig) -> Evaluator:
    def length_evaluator(run: Run, example: Example) -> EvalResult:
        output = run.outputs.get("output") if run.outputs is not None else None
        if output is None:
            return {"key": "length", "score": False}

        value = evaluator_config["value"]
        score = False

        try:
            if "<=" in value:
                score = len(output) <= int(value.replace("<=", "").strip())
            elif "<" in value:
                score = len(output) < int(value.replace("<", "").strip())
            elif ">=" in value:
                score = len(output) >= int(value.replace(">=", "").strip())
            elif ">" in value:
                score = len(output) > int(value.replace(">", "").strip())
            else:
                raise ValueError
        except Exception:
            print(f"[Warning] Invalid integer value in evaluator_config['value']: {value}")
            return {"key": "length", "score": False}

        return {"key": "length", "score": score}

    return length_evaluator


def create_llm_judge_evaluator(evaluator_config: BuiltinEvaluatorConfig) -> Evaluator:
    def llm_judge_evaluator(run: Run, example: Example) -> EvalResult:
        judge_provider = evaluator_config.get("judge_provider")
        if judge_provider is None or ("id" not in judge_provider) or ("config" not in judge_provider):
            raise ValueError("Please provide llm-judge judge_provider id and config")
        judge_model_id = judge_provider["id"]
        judge_model = getattr(ChatModelName, judge_model_id, None)

        temperature = judge_provider["config"]["temperature"]
        if judge_model is not None:
            model = ChatModel(default_model_name=judge_model, temperature=temperature, verbose=True)
        else:
            raise ValueError(f"Invalid judge model_id: {judge_model_id}")
        evaluate_prompt = """Evaluate and give a score between 0 to 1 the following text with the evaluation perspective specified in the prompt.

          evaluation perspective: {evaluation_perspective}
          text: {text}

          only output the score
          """

        prompt = PromptTemplate.from_template(evaluate_prompt)
        inputs = {
            "evaluation_perspective": evaluator_config["value"],
            "text": run.outputs.get("output") if run.outputs is not None else None,
        }

        key = evaluator_config.get("label", "llm-judge")
        score = float(model.invoke(prompt=prompt, **inputs))  # type: ignore[arg-type]
        return {"key": key, "score": score}

    return llm_judge_evaluator


def create_similar_evaluator() -> Evaluator:
    def similar_evaluator(run: Run, example: Example) -> EvaluationResult | EvaluationResults:
        evaluator = LangChainStringEvaluator("embedding_distance")
        run_evaluator = evaluator.as_run_evaluator()
        evaluation_result = run_evaluator.evaluate_run(run, example)
        return evaluation_result

    return similar_evaluator


def generate_builtin_evaluator_functions(
    evaluator_configs: list[BuiltinEvaluatorConfig],
) -> list[Evaluator]:
    evaluators = []

    for evaluator_config in evaluator_configs:
        if evaluator_config["type"] == "length":
            evaluators.append(create_length_evaluator(evaluator_config))
        elif evaluator_config["type"] == "llm-judge":
            evaluators.append(create_llm_judge_evaluator(evaluator_config))
        elif evaluator_config["type"] == "similar":
            evaluators.append(create_similar_evaluator())
        else:
            print(f"[Warning] Unknown evaluator type: {evaluator_config['type']}")

    return evaluators
