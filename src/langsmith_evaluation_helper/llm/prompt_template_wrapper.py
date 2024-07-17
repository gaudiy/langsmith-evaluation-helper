# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Generic, TypeVar

from pydantic import BaseModel

PromptInput = TypeVar("PromptInput", bound=BaseModel)


class InputTypedPromptTemplate(BaseModel, Generic[PromptInput]):
    template: str
    input: PromptInput
