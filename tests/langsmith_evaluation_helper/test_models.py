# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from langchain.prompts import PromptTemplate

from .config_input import Configurations
from langsmith_evaluation_helper.llm.model import ChatModel, ChatModelName
from langsmith_evaluation_helper.loader import load_config


@pytest.fixture
def prompt_fixture():
    return "This is a test prompt"


@pytest.mark.integration_test
@pytest.mark.parametrize("config", Configurations.get_config("multi-providers-all"))
def test_models(config, prompt_fixture, create_temp_config_file):
    config_file_path = create_temp_config_file(config_content=config)
    config_file = load_config(str(config_file_path))
    for model_config in config_file["providers"]:
        model_id = model_config["id"]
        config = model_config.get("config", {})
        azure_deployment = config.get("azure_deployment", None)
        azure_api_version = config.get("azure_api_version", None)
        if ("AZURE" in model_id) and (azure_deployment is None or azure_api_version is None):
            raise ValueError("Add azure_deployment and azure_api_version to config for Azure GPT models")

        model = getattr(ChatModelName, model_id, None)

        message = PromptTemplate.from_template(template=prompt_fixture)
        if model is not None:
            llm = ChatModel(
                default_model_name=model,
                temperature=0,
                azure_deployment=azure_deployment,
                api_version=azure_api_version,
                verbose=True,
            )
        else:
            raise ValueError(f"Invalid model_id: {model_id}")
        result = llm.invoke(message)
        print(f"{model_id} : {result}", end="\n")
        assert isinstance(result, str)
