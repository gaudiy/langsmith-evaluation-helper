# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

import os
from enum import Enum
from typing import Any

from langchain.chat_models.base import BaseChatModel
from langchain.schema.output_parser import StrOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import SecretStr
from langchain_core.runnables import RunnableConfig
from langchain_google_vertexai import ChatVertexAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI


class ChatModelName(Enum):
    TURBO = "gpt-3.5-turbo"
    GPT4 = "gpt-4-0613"
    GPT4_32K = "gpt-4-32k-0613"
    GPT4O = "gpt-4o"
    AZURE_GPT35_16K_TURBO = "gpt-35-turbo"
    AZURE_GPT4_32K = "gpt-4-32k"
    GEMINI_PRO = "gemini-pro"
    GEMINI_FLASH = "gemini-1.5-flash-001"
    CLAUDE3_SONNET = "claude3-sonnet"
    CLAUDE3_OPUS = "claude-3-opus-20240229"
    CLAUDE3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE3_5_SONNET = "claude-3-5-sonnet-20240620"


AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE", "")


def get_chat_model(name: ChatModelName, **kwargs: Any) -> BaseChatModel:
    azure_deployment = kwargs.pop("azure_deployment") if "azure_deployment" in kwargs else None
    api_version = kwargs.pop("api_version") if "api_version" in kwargs else None
    if (
        name == ChatModelName.TURBO
        or name == ChatModelName.GPT4
        or name == ChatModelName.GPT4_32K
        or name == ChatModelName.GPT4O
    ):
        return ChatOpenAI(model=name.value, **kwargs)
    elif (
        name == ChatModelName.AZURE_GPT35_16K_TURBO
        and ((azure_deployment is not None) and (api_version is not None))
        or name == ChatModelName.AZURE_GPT4_32K
        and ((azure_deployment is not None) and (api_version is not None))
    ):
        return AzureChatOpenAI(
            api_key=SecretStr(AZURE_OPENAI_API_KEY),
            azure_endpoint=AZURE_OPENAI_API_BASE,
            api_version=api_version,
            azure_deployment=azure_deployment,
            **kwargs,
        )
    elif name == ChatModelName.GEMINI_PRO or name == ChatModelName.GEMINI_FLASH:
        return ChatVertexAI(
            model_name=name.value,
            **kwargs,
        )
    elif (
        name == ChatModelName.CLAUDE3_SONNET
        or name == ChatModelName.CLAUDE3_OPUS
        or name == ChatModelName.CLAUDE3_HAIKU
        or name == ChatModelName.CLAUDE3_5_SONNET
    ):
        return ChatAnthropic(model_name="claude-3-sonnet-20240229", **kwargs)
    else:
        raise ValueError(f"Invalid model name. {name}")


class ChatModel:
    """Facade wrapper class to handle lifecycle of Langchain's basechatmodel."""

    default_model: BaseChatModel
    default_model_name: ChatModelName
    verbose: bool = True
    kwargs: Any

    def __init__(
        self,
        default_model_name: ChatModelName = ChatModelName.CLAUDE3_SONNET,
        **kwargs: Any,
    ) -> None:
        self.default_model = get_chat_model(default_model_name, **kwargs)
        self.default_model_name = default_model_name
        self.kwargs = kwargs

    def get_model(self, model_name: ChatModelName | None = None) -> BaseChatModel:
        model = self.default_model
        if model_name:
            model = get_chat_model(model_name, **self.kwargs)

        return model

    def invoke(
        self,
        prompt: PromptTemplate,
        tags: list[str] | None = None,
        model_name: ChatModelName | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        chain = (prompt | self.get_model(model_name)) | StrOutputParser()
        config = RunnableConfig(
            tags=tags or [],
            metadata=metadata or {},
        )

        return chain.invoke(input=kwargs, config=config)

    async def async_invoke(
        self,
        prompt: PromptTemplate,
        tags: list[str] | None = None,
        model_name: ChatModelName | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        chain = prompt | self.get_model(model_name) | StrOutputParser()
        config = RunnableConfig(
            tags=tags or [],
            metadata=metadata or {},
        )

        return await chain.ainvoke(input=kwargs, config=config)
