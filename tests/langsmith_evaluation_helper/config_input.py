# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0


class Configurations:
    _configs = {
        "single_provider": """
        description: Testing1 single provider

        prompt:
          name: prompt.py
          type: python
          entry_function: test_function1

        evaluators_file_path: test_evaluation1.py

        providers:
          - id: Model1
            config:
              temperature: 0.7

        tests:
          dataset_name: dataset1
          experiment_prefix: test
        """,
        "multi_provider": """
        description: Testing2 multi-provider

        prompt:
          name: prompt.py
          type: python
          entry_function: test_function1

        evaluators_file_path: test_evaluation1.py

        providers:
          - id: Model1
            config:
              temperature: 0.7
          - id: Model2
            config:
              temperature: 0.7

        tests:
          dataset_name: dataset1
          experiment_prefix: test
        """,
        "assert_built_in_evaluator": """
        description: Testing3 Assert Builtin Evaluators

        prompt:
          name: prompt.py
          type: python
          entry_function: test_function1

        evaluators_file_path: test_evaluation1.py

        providers:
          - id: Model1
            config:
              temperature: 0.7
          - id: Model2
            config:
              temperature: 0.7

        tests:
            dataset_name: Toxic Queries
            experiment_prefix: config_prompt_1
            max_concurrency: 4
            assert:
                - type: length
                  value: "<= 200"
        """,
        "multiple_asserts": """
        description: Testing3 Multiple Asserts

        prompt:
          name: prompt.py
          type: python
          entry_function: test_function1

        evaluators_file_path: test_evaluation1.py

        providers:
          - id: Model1
            config:
              temperature: 0.7
          - id: Model2
            config:
              temperature: 0.7

        tests:
            dataset_name: Toxic Queries
            experiment_prefix: config_prompt_1
            max_concurrency: 4
            assert:
                - type: length
                  value: "<= 200"
                - type: 'llm-judge'
                  value: "Is this Toxic"
                  judge_provider:
                    id: TURBO
                    config:
                       temperature: 0.7
                - type: 'similar'
        """,
        "split_no_limit": """
        description: Testing load_dataset with  split no limit

        prompt:
          name: prompt.py
          type: python
          entry_function: test_function1

        evaluators_file_path: test_evaluation1.py

        providers:
          - id: Model1
            config:
              temperature: 0.7
          - id: Model2
            config:
              temperature: 0.7

        tests:
            dataset_name: Toxic Queries
            experiment_prefix: config_prompt_1
            max_concurrency: 4
            split: base
            assert:
                - type: length
                  value: "<= 200"
                - type: 'similar'
                - type: 'llm-judge'
                  value: "Is this Toxic"
        """,
        "limit_no_split": """
        description: Testing load_dataset with limit, no split

        prompt:
          name: prompt.py
          type: python
          entry_function: test_function1

        evaluators_file_path: test_evaluation1.py

        providers:
          - id: Model1
            config:
              temperature: 0.7
          - id: Model2
            config:
              temperature: 0.7

        tests:
            dataset_name: Toxic Queries
            experiment_prefix: config_prompt_1
            max_concurrency: 4
            limit: 2
            assert:
                - type: length
                  value: "<= 200"
                - type: 'similar'
                - type: 'llm-judge'
                  value: "Is this Toxic"
        """,
        "limit_split": """
        description: Testing load_dataset with limit, split

        prompt:
          name: prompt.py
          type: python
          entry_function: test_function1

        evaluators_file_path: test_evaluation1.py

        providers:
          - id: Model1
            config:
              temperature: 0.7
          - id: Model2
            config:
              temperature: 0.7

        tests:
            dataset_name: Toxic Queries
            experiment_prefix: config_prompt_1
            max_concurrency: 4
            split: base
            limit: 1
            assert:
                - type: length
                  value: "<= 200"
                - type: 'similar'
                - type: 'llm-judge'
                  value: "Is this Toxic"
        """,
        "multi-providers-all": """
        description: Testing all various providers.

        prompt:
          name: prompt.py
          type: python
          entry_function: test_function1

        evaluators_file_path: test_evaluation1.py

        providers:
          - id: TURBO
            config:
              temperature: 0.7
          - id: GPT4
          - id: GPT4O
          - id: AZURE_GPT35_16K_TURBO
            config:
              temperature: 0.7
              azure_deployment: gpt-35-turbo-16k-dev
              azure_api_version: 2023-08-01-preview
          # - id: GEMINI_PRO
          # - id: GEMINI_FLASH
          - id: CLAUDE3_SONNET
          - id: CLAUDE3_OPUS
          - id: CLAUDE3_HAIKU
          - id: CLAUDE3_5_SONNET



        tests:
            dataset_name: Toxic Queries
            experiment_prefix: config_prompt_1
            max_concurrency: 4
            split: base
            limit: 1

        """,
        "custom_run": """
        description: Testing load_dataset with limit, split

        evaluators_file_path: test_evaluation1.py

        custom_run:
          file_path: custom_run.py
          entry_function: custom_run

        providers:
          - id: Model1
            config:
              temperature: 0.7

        tests:
            dataset_name: Toxic Queries
            experiment_prefix: config_prompt_1
        """,
        "integration_loader": """
        description: End to end integration test

        prompt:
          name: prompt.py
          type: python
          entry_function: toxic_example_prompts

        evaluators_file_path: evaluations.py

        providers:
          - id: TURBO
            config:
              temperature: 0.7

        tests:
            dataset_name: Toxic Queries
            experiment_prefix: toxic_queries
    """,
    }

    @classmethod
    def get_config(cls, config_names: str | list[str]):
        if isinstance(config_names, str):
            return [cls._configs.get(config_names)]

        if isinstance(config_names, list):
            return [cls._configs.get(name) for name in config_names]

        raise ValueError("config_names must be a string or a list of strings")

    @classmethod
    def get_all_configs(cls):
        return list(cls._configs.values())
