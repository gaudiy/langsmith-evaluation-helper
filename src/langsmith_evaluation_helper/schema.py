# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from typing import TypedDict


class ProviderConfig(TypedDict):
    temperature: float


class Provider(TypedDict):
    id: str
    config: ProviderConfig
