# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

# Assuming Configurations.get_all_configs(), MockClient, response_examples, load_config, and load_dataset are defined elsewhere


@pytest.fixture(scope="session")
def create_temp_config_file(tmp_path_factory):
    base_temp = tmp_path_factory.mktemp("data")

    def _create_temp_config_file(config_content: str) -> Path:
        config_file_path = base_temp / "config.yml"
        config_file_path.write_text(config_content)
        return config_file_path

    return _create_temp_config_file
