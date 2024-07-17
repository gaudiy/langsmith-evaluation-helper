# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

import importlib.util
import inspect
from collections.abc import Callable
from typing import Any


def is_async_function(func: Callable[..., Any]) -> bool:
    return inspect.iscoroutinefunction(func) or inspect.isasyncgenfunction(func)


def load_function(module_path: str, function_name: str) -> Any:
    """
    Dynamically load a function from a given module.
    """
    if not isinstance(module_path, str) or not module_path:
        raise ValueError("Invalid or empty module path.")
    if not isinstance(function_name, str) or not function_name:
        raise ValueError("Invalid or empty function name.")

    try:
        spec = importlib.util.spec_from_file_location("module", module_path)
        if spec is None:
            raise ImportError(f"Cannot find module specification for the path: {module_path}")

        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            raise ImportError("Module loader is not available.")
        spec.loader.exec_module(module)

        if not hasattr(module, function_name):
            raise AttributeError(f"Function '{function_name}' not found in module '{module_path}'")
    except (ImportError, AttributeError) as error:
        print(f"Error: {error}")
        raise
    return getattr(module, function_name)
