# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

from langsmith.schemas import Run, Example
from uuid import uuid4
from datetime import datetime


def run_factory(name: str = "", inputs: dict = {}, outputs: dict = {}) -> Run:
    return Run(
        id=str(uuid4()),
        name=name,
        start_time=datetime.now(),
        run_type="test_type",
        trace_id=str(uuid4()),
        inputs={},
        outputs=outputs,
    )


def example_factory(inputs: dict = {}, outputs: dict = {}) -> Example:
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
