# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from langsmith.schemas import Example, Run


def fetch_output_message(run: Run) -> str | None:
    """Helper function to fetch the output message from the run or raise an error if not present."""
    if run.outputs is None:
        raise ValueError("run.outputs is None")
    output_message = run.outputs.get("output")
    if output_message is None:
        return None
    return output_message


def correct_label(run: Run, example: Example) -> dict:
    output_message = fetch_output_message(run)
    ref_label = None
    if output_message is None:
        return {"score": False}
    if example is not None and example.outputs is not None:
        try:
            ref_label = example.outputs.get("output_label")
        except Exception as e:
            print(e)
    score = output_message == ref_label
    return {"score": score}


evaluators: list[Any] = [correct_label]
summary_evaluators: list[Any] = []
