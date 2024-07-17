# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

import inspect
import os
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any

from langchain.prompts import PromptTemplate
from langsmith import traceable

from langsmith_evaluation_helper.llm.model import ChatModel, ChatModelName
from langsmith_evaluation_helper.llm.prompt_template_wrapper import (
    InputTypedPromptTemplate,
)
from langsmith_evaluation_helper.utils import is_async_function, load_function


def load_prompt(config_path: str, config: dict[Any, Any]) -> Any:
    """
    Load the config file and execute the specified entry function.
    """
    prompt_info = config["prompt"]
    script_path = os.path.join(os.path.dirname(config_path), prompt_info["name"])
    function_name = prompt_info["entry_function"]

    func = load_function(script_path, function_name)

    return func


def has_inputs_argument(func: Callable[..., Any]) -> bool:
    signature = inspect.signature(func)
    parameters = signature.parameters
    return "inputs" in parameters


def get_prompt_template_and_kwargs_from_input_typed_prompt_template(
    prompt: InputTypedPromptTemplate,
) -> tuple[PromptTemplate, dict[str, Any]]:
    return PromptTemplate.from_template(prompt.template), prompt.input.model_dump()


def get_prompt_template_and_kwargs_from_inputs(
    prompt: str, inputs: dict[Any, Any]
) -> tuple[PromptTemplate, dict[str, Any]]:
    kwargs: dict[str, Any] = {}
    for key, _ in inputs.items():
        kwargs[key] = inputs.get(key, "Unknown")

    return PromptTemplate.from_template(prompt), kwargs


@traceable
def execute_prompt(
    inputs: dict[Any, Any],
    prompt: str | InputTypedPromptTemplate,
    provider: dict[Any, Any],
) -> str:
    if isinstance(prompt, str):
        _prompt_template, kwargs = get_prompt_template_and_kwargs_from_inputs(prompt, inputs)
    elif isinstance(prompt, InputTypedPromptTemplate):
        _prompt_template, kwargs = get_prompt_template_and_kwargs_from_input_typed_prompt_template(prompt)
    else:
        raise ValueError(f"Invalid prompt type: {type(prompt)}")

    messages = _prompt_template.format(**kwargs)
    formatted_messages = PromptTemplate.from_template(messages)

    model_id = provider["id"]
    model = getattr(ChatModelName, model_id, None)
    provider_config = provider.get("config", {})
    temperature = provider_config.get("temperature", 0)
    azure_deployment = provider_config.get("azure_deployment", None)
    azure_api_version = provider_config.get("azure_api_version", None)
    if ("AZURE" in model_id) and (azure_deployment is None or azure_api_version is None):
        raise ValueError("Add azure_deployment and azure_api_version to config for Azure GPT models")
    if model is not None:
        llm = ChatModel(
            default_model_name=model,
            temperature=temperature,
            azure_deployment=azure_deployment,
            api_version=azure_api_version,
            verbose=True,
        )
    else:
        raise ValueError(f"Invalid model_id: {model_id}")
    result = llm.invoke(formatted_messages)
    return result


def load_prompt_template(
    config_path: str, prompt_config: dict[Any, Any], provider: dict[Any, Any]
) -> Callable[[dict[str, Any]], str] | Callable[[dict[str, Any]], Awaitable[str]]:
    prompt_func = load_prompt(config_path, prompt_config)
    is_async = is_async_function(prompt_func)
    has_inputs = has_inputs_argument(prompt_func)

    async def run_async(inputs: dict[str, Any]) -> str:
        prompt = await prompt_func(inputs) if has_inputs else await prompt_func()
        return execute_prompt(inputs, prompt, provider)

    def run_sync(inputs: dict[str, Any]) -> str:
        prompt = prompt_func(inputs) if has_inputs else prompt_func()
        return execute_prompt(inputs, prompt, provider)

    return run_async if is_async else run_sync


def load_prompt_function(
    config_path: str,
    prompt_file_name: str,
    entry_function_name: str,
    provider: dict[Any, Any],
) -> Callable[[dict[str, Any]], Any] | Callable[[dict[str, Any]], Coroutine[Any, Any, Any]]:
    script_path = os.path.join(os.path.dirname(config_path), prompt_file_name)
    function_name = entry_function_name
    prompt_func = load_function(script_path, function_name)
    is_async = is_async_function(prompt_func)
    params = inspect.signature(prompt_func).parameters

    def create_kwargs(inputs: dict[Any, Any]) -> dict[str, Any]:
        kwargs = {}
        if "inputs" in params:
            kwargs["inputs"] = inputs
        if "provider" in params:
            kwargs["provider"] = provider
        return kwargs

    if is_async:

        async def arun(inputs: dict[Any, Any]) -> Any:
            return await prompt_func(**create_kwargs(inputs))

        return arun

    def run(inputs: dict[Any, Any]) -> Any:
        return prompt_func(**create_kwargs(inputs))

    return run


def load_run_function(
    config_path: str, config: dict[Any, Any], provider: dict[Any, Any]
) -> Callable[[dict[Any, Any]], Any]:
    prompt_config = config.get("prompt")
    custom_run_config = config.get("custom_run")

    if prompt_config is not None and custom_run_config is not None:
        raise ValueError("prompt and custom_run cannot be specified simultaneously")

    if custom_run_config:
        return load_prompt_function(
            config_path,
            custom_run_config["file_path"],
            custom_run_config["entry_function"],
            provider,
        )
    else:
        return load_prompt_template(config_path, config, provider)
