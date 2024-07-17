# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
import sys
from typing import Any

import yaml
from langsmith import Client, aevaluate, evaluate

from langsmith_evaluation_helper.builtin_evaluators import (
    generate_builtin_evaluator_functions,
)
from langsmith_evaluation_helper.load_run_function import load_run_function
from langsmith_evaluation_helper.utils import is_async_function, load_function

LANGCHAIN_TENANT_ID = os.getenv("LANGCHAIN_TENANT_ID", None)
MAX_EXAMPLES_COUNT = 1000


def load_config(config_path: Any) -> dict[str, Any]:
    """
    Loads config file as YML dictionary.
    """
    with open(config_path) as file:
        config = yaml.safe_load(file)
    return config


def load_dataset(config: dict[Any, Any]) -> tuple[Any, Any, Any]:
    test_info = config["tests"]

    dataset_name = test_info["dataset_name"]
    experiment_prefix = test_info["experiment_prefix"]
    num_repetitions = test_info.get("num_repetitions", 1)
    split_string = test_info.get("split", None)
    limit = test_info.get("limit", None)

    if split_string is None and limit is None:
        return dataset_name, experiment_prefix, num_repetitions
    limit = int(limit) if limit is not None else MAX_EXAMPLES_COUNT

    client = Client()
    examples = list(client.list_examples(dataset_name=dataset_name))

    if split_string is None and limit > 0:
        return examples[:limit], experiment_prefix, num_repetitions

    splits = set(split_string.split(" "))

    test_examples = [
        example
        for example in examples
        if example.metadata is not None
        and example.metadata.get("dataset_split", None) is not None
        and bool(splits & set(example.metadata["dataset_split"]))
    ]

    test_examples = test_examples[:limit]

    if len(test_examples) > 0:
        return (test_examples, experiment_prefix, num_repetitions)
    else:
        raise ValueError(f"No examples found for the dataset split: {split_string}")


def load_evaluators(config: dict[Any, Any]) -> tuple[Any, Any]:
    builtin_evaluators_config = config["tests"].get("assert", [])
    builtin_evaluators = generate_builtin_evaluator_functions(builtin_evaluators_config)

    evaluators_file_path = os.path.join(os.path.dirname(config_path), config["evaluators_file_path"])
    evaluators = load_function(evaluators_file_path, "evaluators") + builtin_evaluators
    summary_evaluators = load_function(evaluators_file_path, "summary_evaluators")

    return evaluators, summary_evaluators


async def run_evaluate(
    provider: dict[Any, Any],
    experiment_prefix: str,
    num_repetitions: int,
    **kwargs: dict[str, Any],
) -> tuple[Any, Any]:
    experiment_prefix_provider = experiment_prefix + provider["id"]
    prompt_func = load_run_function(config_path, config_file, provider)

    is_async = is_async_function(prompt_func)

    common_args = {
        "experiment_prefix": experiment_prefix_provider,
        "num_repetitions": num_repetitions,
        "metadata": {
            "prompt_version": "1",
        },
        **kwargs,
    }

    if is_async:
        result = await aevaluate(prompt_func, **common_args)
        dataset_id = await result._manager.get_dataset_id()
    else:
        result = evaluate(prompt_func, **common_args)
        dataset_id = result._manager.dataset_id
    experiment_id = None
    if result._manager and result._manager._experiment and result._manager._experiment.id is not None:
        experiment_id = result._manager._experiment.id.__str__()

    return dataset_id, experiment_id


async def main(config_file: dict[Any, Any]) -> None:
    dataset_name, experiment_prefix, num_repetitions = load_dataset(config_file)
    evaluators, summary_evaluators = load_evaluators(config_file)
    max_concurrency = config_file["tests"].get("max_concurrency", None)
    providers = config_file["providers"]

    dataset_id = None
    experiment_ids = []

    tasks = [
        run_evaluate(
            provider,
            experiment_prefix,
            data=dataset_name,
            evaluators=evaluators,
            summary_evaluators=summary_evaluators,
            max_concurrency=max_concurrency,
            num_repetitions=num_repetitions,
        )
        for provider in providers
    ]

    # Run all tasks concurrently using asyncio.gather
    results = await asyncio.gather(*tasks)

    # Unpack results and collect dataset and experiment IDs
    for _dataset_id, experiment_id in results:
        dataset_id = _dataset_id
        experiment_ids.append(experiment_id)

    # Print the final comparison URL if there are multiple providers
    if len(providers) > 1:
        seed_url = "https://smith.langchain.com/o/"
        experiment_id_query_str = "%2C".join(experiment_ids)

        url = (
            f"{seed_url}{LANGCHAIN_TENANT_ID}/datasets/{dataset_id}/compare?selectedSessions={experiment_id_query_str}"
        )
        print(url)


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yml"
    config_file = load_config(config_path)

    asyncio.run(main(config_file))
