# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from uuid import uuid4

from langsmith.schemas import Example, Run


def run_factory(name: str = "", inputs: dict | None = None, outputs: dict | None = None) -> Run:
    if inputs is None:
        inputs = {}
    if outputs is None:
        outputs = {}

    return Run(
        id=str(uuid4()),
        name=name,
        start_time=datetime.now(),
        run_type="test_type",
        trace_id=str(uuid4()),
        inputs={},
        outputs=outputs,
    )


def example_factory(inputs: dict | None = None, outputs: dict | None = None) -> Example:
    if inputs is None:
        inputs = {}
    if outputs is None:
        outputs = {}

    return Example(
        id=str(uuid4()),
        dataset_id=str(uuid4()),
        created_at=datetime.now(),
        inputs={},
        metadata={},
        modified_at=None,
        outputs=outputs,
        runs=[],
    )
