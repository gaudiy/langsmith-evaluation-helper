# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from langchain.prompts import PromptTemplate

from langsmith_evaluation_helper.llm.model import ChatModel, ChatModelName
from langsmith_evaluation_helper.schema import Provider


def custom_run_example(inputs: dict, provider: Provider) -> str:
    # replace with your favorite way of calling LLM or RAG or anything!
    id = provider.get("id")
    if id is None:
        raise ValueError("Provider ID is required.")

    llm = ChatModel(default_model_name=ChatModelName[id])
    prompt_template = PromptTemplate(
        input_variables=["text"], template="Is this sentence toxic? {text}."
    )
    messages = prompt_template.format(**inputs)
    formatted_messages = PromptTemplate.from_template(messages)

    result = llm.invoke(formatted_messages)

    return result
