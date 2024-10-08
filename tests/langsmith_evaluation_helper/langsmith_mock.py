# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from langsmith.schemas import Example


# Mock Client class of Langsmith
class MockClient:
    def __init__(self: "MockClient", response_examples: list[Example] | None = None) -> None:
        if response_examples is None:
            response_examples = []
        self.response_examples = response_examples

    def list_examples(self, dataset_name: str) -> list[Example]:
        if self.response_examples is None:
            return []
        return self.response_examples
