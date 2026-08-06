# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

import os
from collections.abc import Callable
from pathlib import Path

import pytest

# Assuming Configurations.get_all_configs(), MockClient, response_examples, load_config, and load_dataset are defined elsewhere

# Placeholder credentials so unit tests can construct provider clients without real keys.
PLACEHOLDER_API_KEYS = {"OPENAI_API_KEY": "sk-unit-test"}


@pytest.fixture(autouse=True)
def placeholder_api_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fill in placeholder API keys for any provider credential that is not already set.

    Clients such as `ChatOpenAI` and `OpenAIEmbeddings` validate their API key at construction
    time, so unit tests that never make a request would still fail without one. Real values (from
    `.env` or CI secrets) are left untouched so `integration_test` tests keep hitting the providers.
    """
    for name, placeholder in PLACEHOLDER_API_KEYS.items():
        if not os.getenv(name):
            monkeypatch.setenv(name, placeholder)


@pytest.fixture(scope="session")
def create_temp_config_file(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
    base_temp = tmp_path_factory.mktemp("data")

    def _create_temp_config_file(config_content: str) -> Path:
        config_file_path = base_temp / "config.yml"
        config_file_path.write_text(config_content)
        return config_file_path

    return _create_temp_config_file
