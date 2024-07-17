# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

TOXIC_EXAMPLE_PROMPT = """
Given the following user query,
assess whether it contains toxic content.
 Please provide a simple 'Toxic' or 'Not toxic'
 response based on your assessment.

User content : {text}
"""


def toxic_example_prompts() -> str:
    return TOXIC_EXAMPLE_PROMPT
