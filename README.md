# LangSmith Evaluation Helper

![CI](https://github.com/gaudiy/langsmith-evaluation-helper/actions/workflows/pr-check.yml/badge.svg)

Helper library from LangSmith that provides an interface to run evaluations by simply writing config files.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Sample config.yml file.](#sample-configyml-file)
    - [Configuration file description](#configuration-file-description)
      - [**`description`**](#description)
      - [**`prompt`**](#prompt)
      - [**`custom_run`**](#custom_run)
      - [**`evaluators_file_path`**](#evaluators_file_path)
      - [**`providers`**](#providers)
      - [**`tests`**](#tests)
    - [Supported Models and IDs](#supported-models-and-ids)
  - [How to run](#how-to-run)
    - [CLI Options.](#cli-options)
  - [Cookbooks](#cookbooks)
- [Setup for developers](#setup-for-developers)
  - [Requirements](#requirements)
  - [Setup](#setup)
  - [Create a virtual environment](#create-a-virtual-environment)
  - [Install dependencies](#install-dependencies)
  - [Install package locally](#install-package-locally)
  - [Run](#run)
  - [Pytest Tools](#pytest-tools)
    - [Code coverage](#code-coverage)
    - [For only the unit test](#for-only-the-unit-test)
    - [For all test including unit and integration test](#for-all-test-including-unit-and-integration-test)
  - [Modifying README](#modifying-readme)
    - [Install doctoc](#install-doctoc)
    - [Run doctoc](#run-doctoc)
- [Contribution](#contribution)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Quick Start

### Installation
To get started, [install the package](https://pypi.org/project/langsmith-evaluation-helper/), then follow the instructions in the [Configuration Section](#configuration) and [Run Section](#how-to-run)

```
pip install langsmith-evaluation-helper
```

### Configuration
Capabilities of `config.yml` file.

#### Sample config.yml file.

```yml
description: config for conversation prompt

prompt:
  name: prompt.py
  type: python
  entry_function: toxic_example_prompts

# Config when you want to run with function
# This cannot be specified with "prompt" simaltaneously
# custom_run:
#   file_path: custom_run.py
#   entry_function: toxic_example_prompts

evaluators_file_path: evaluations.py

providers:
  - id: TURBO
    config:
      temperature: 0.7
  - id: CLAUDE3_SONNET
    config:
      temperature: 0.7

tests:
  dataset_name: Toxic Queries
  experiment_prefix: config_prompt_1
  max_concurrency: 4

  assert:
    - type: length
      value: "<= 200"
    - type: llm-judge
      value: "Is this toxic?"
      judge_provider:
        id: TURBO
        config:
          temperature: 0.7
```

#### Configuration file description

##### **`description`**

| **Configuration Element** | **Purpose**                                            | **Example**                                   | **Notes**                                                            |
| ------------------------- | ------------------------------------------------------ | --------------------------------------------- | -------------------------------------------------------------------- |
| **`description`**         | Provides a general overview of the configuration file. | `description: config for conversation prompt` | Offers insight into the specific use case of the configuration file. |

##### **`prompt`** 
Defines the prompt script's name, type, and entry function.

| **Configuration Element** | **Purpose**                                                                | **Example**                             | **Notes**                                                                                                                                                     |
| ------------------------- | -------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                    | Specifies the filename containing the prompt logic.                        | `name: prompt.py`                       | - The name (or relative path to `config.yml`) of the Python script containing the prompt definitions.                                                         |
| `type`                    | Identifies the language or framework used in the prompt logic.             | `type: python`                          | Currently, only Python is supported.                                                                                                                          |
| `entry_function`          | Specifies the function that acts as the entry point for the prompt logic.  | `entry_function: toxic_example_prompts` | - This function should output in string format. <br> - The function is defined in `prompt.py`.                                                                |

##### **`custom_run`**
Defines a custom execution script for more complex or specialized evaluation logic.

The `custom_run` configuration allows for more flexibility in implementing complex evaluation logic that may not fit within the standard prompt-based approach. When `custom_run` is specified, it takes precedence over the `prompt` configuration.

| **Configuration Element** | **Purpose**                                                                | **Example**                             | **Notes**                                                                                                                                                     |
| ------------------------- | -------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `file_path`                    | Specifies the filename containing the custom execution logic.              | `name: custom_evaluator.py`             | - The name (or relative path to `config.yml`) of the Python script containing the custom execution logic.                                                     |
| `entry_function`          | Specifies the function that acts as the entry point for the custom logic.  | `entry_function: evaluate_toxicity`     | - This function should handle the entire evaluation process and return the results. <br> - The function is defined in the script specified by `name`.         |


##### **`evaluators_file_path`**

| **Configuration Element**  | **Purpose**                                       | **Example**                            | **Notes**                                                    |
| -------------------------- | ------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------ |
| **`evaluators_file_path`** | Points to the file that contains evaluator logic. | `evaluators_file_path: evaluations.py` | - Contains functions to evaluate or validate prompt outputs. |

##### **`providers`** 
Lists different models (LLMs) or services used for the conversation prompt.

| **Configuration Element** | **Purpose**                                                         | **Example**        | **Notes**                                                                                                                                                                                                                                      |
| ------------------------- | ------------------------------------------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                      | Unique identifier for the provider.                                 | `id: TURBO`        | - Could be a model name, version, or some unique identifier. <br> - **Supported IDs:** <br> - `TURBO = "gpt-3.5-turbo"`.<br>For a list of supported models and their IDs, see the [Supported Models and IDs](#supported-models-and-ids) table. |
| `config`                  | Holds specific settings for the model/service.                      |                    |                                                                                                                                                                                                                                                |
| `temperature`             | Controls the randomness of the output.                              | `temperature: 0.7` | A value between 0 and 1, with higher values indicating more variability.                                                                                                                                                                       |
| `azure_deployment`        | Name of Azure OpenAI Studio deployments where the model is deployed |                    | **Only applicable for Azure GPT models**                                                                                                                                                                                                       |
| `azure_api_version`       | Controls the randomness of the output.                              |                    | **Only applicable for Azure GPT models**                                                                                                                                                                                                       |

##### **`tests`** 
Defines the parameters for running tests on the conversation prompts.

| **Configuration Element** | **Purpose**                                                         | **Example**                          | **Notes**                                                |
| ------------------------- | ------------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------------- |
| `dataset_name`            | The name of the dataset to be used in testing.                      | `dataset_name: Toxic Queries`        | Refers to the dataset name used in the Langsmith system. |
| `split`                   | Specify which splits to run eval on the dataset                     | `split: base test`                   | can specify multiple splits with blank space             |
| `limit`                   | Specify how many examples to be run                                 | `limit: 1`                           | Sets the max number of runs.                             |
| `experiment_prefix`       | Prefix for naming experiments.                                      | `experiment_prefix: config_prompt_1` | Sets a prefix to distinguish experiments.                |
| `max_concurrency`         | Number of tests or evaluations that can run concurrently.           | `max_concurrency: 4`                 | Determines how many tests can be run in parallel.        |
| `num_repetitions`         | Specify how many times to run/evaluate each example in your dataset | `num_repetitions: 3`                 |                                                          |
| **`assert`**              | Specifies validation criteria for test results.                     |                                      |                                                          |
| `type`                    | Type of assertion to validate the results.                          | `type: length`                       | Type of assertion                                        |
| `value`                   | Defines the validation condition.                                   | `value: "<= 200"`                    | the condition of assertion metrics                       |
| `label`                   | Label of metric                                                     | `Correct`                            |                                                          |

`assert` types

| **Type**    | **description**                                             | **value example**                    |
| ----------- | ----------------------------------------------------------- | ------------------------------------ |
| `length`    | check length of output satisfies the condition specified    | "<= 200", "< 200", ">= 200", "> 200" |
| `llm-judge` | run LLM to evaluate with the perspective specified in value | "Is this toxic?"                     |
| `similar`   | check similarity of output to reference output in dataset   | N/A                                  |

Additional fields in case of `llm-judge` assert type.

`judge_provider` Models (LLM) or service used for the llm-judge.

| **Configuration Element** | **Purpose**                                    | **Example**        | **Notes**                                                                                                                                                                                                                                      |
| ------------------------- | ---------------------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                      | Unique identifier for the provider.            | `id: TURBO`        | - Could be a model name, version, or some unique identifier. <br> - **Supported IDs:** <br> - `TURBO = "gpt-3.5-turbo"`.<br>For a list of supported models and their IDs, see the [Supported Models and IDs](#supported-models-and-ids) table. |
| `config`                  | Holds specific settings for the model/service. |                    |                                                                                                                                                                                                                                                |
| `temperature`             | Controls the randomness of the output.         | `temperature: 0.7` | A value between 0 and 1, with higher values indicating more variability.                                                                                                                                                                       |

> Note: <br> - Currently, only Python files saved in the same directory as `config.yml` are supported.

#### Supported Models and IDs

| **ID**                | **Model Name**   |
| --------------------- | ---------------- |
| TURBO                 | `gpt-3.5-turbo`  |
| GPT4                  | `gpt-4-0613`     |
| CLAUDE3_SONNET        | `claude3-sonnet` |
| GPT4_32K              | `gpt-4-32k-0613` |
| GEMINI_PRO            | `gemini-pro`     |
| AZURE_GPT35_16K_TURBO | `gpt-35-turbo`   |
| AZURE_GPT4_32K        | `gpt-4-32k`      |


### How to run

1. Create a config.yml file. Refer to samples [here](cookbook/experiment).
2. Run the command with the config file 
```
langsmith-evaluation-helper evaluate cookbook/experiment/cookbook/experiment/toxic_query/config_basic.yml
```
3. Check evaluation results from the link in the output
```
View the evaluation results for experiment: 'toxic_queriesTURBO-...' at:

https://smith.langchain.com/o/...
```

#### CLI Options.

| Options                | Description             | Usage                                |
| ---------------------- | ----------------------- | ------------------------------------ |
| `<path/to/config.yml>` | Path to config.yml file | `langsmith-evaluation-helper evaluate <path/to/config.yml>` |

### Cookbooks

Get started with some use-cases for the library over at [cookbooks](/cookbook/)

## Setup for developers

### Requirements

- Python 3.11.3
- [direnv](https://github.com/direnv/direnv)
- [uv](https://github.com/astral-sh/uv)

### Setup

Install uv:

```
# With pip
pip install uv

# With Homebrew.
brew install uv
```


### Create a virtual environment
Create a virtual environment at .venv. with a particular version of python, eg python3.11

```
uv venv --python=$(which python3.11)
```

To activate the virtual environment:

```
source .venv/bin/activate
```


### Install dependencies
For intial installation, compile from pyproject.toml to requiremts.txt
```
uv pip compile --extra=dev -o requirements.txt pyproject.toml
```

Next, install them. Synchronize the environment with the specified requirements
```
uv pip sync requirements.txt
```

If you want to upgrade specific package:
```
uv pip compile --upgrade-package=langchain --extra=dev -o requirements.txt pyproject.toml
```

### Install package locally

Install the package in editable mode for development
```
uv pip install -e .
```

### Run
For the package to run, it will require langchain API key and required model's API keys such as OpenAI's Keys. 

1. Save the API keys in the .env file

2. Make the `.env` file accessable to `direnv`. Note: if you are using zsh, run 
```
eval "$(direnv hook zsh)"
direnv allow .
```

Follow the same steps as [How to run](#how-to-run)


### Pytest Tools 
#### Code coverage
```
pytest --cov=langsmith_evaluation_helper
```
#### For only the unit test 
```
make test
```
#### For all test including unit and integration test 
```
make all_test
```
### Modifying README
#### Install doctoc

You can use [doctoc](https://github.com/thlorenz/doctoc) to auto-generate (or modify) the table of contents.

1. To install doctoc, you first need to install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
2. Install [doctoc](https://github.com/thlorenz/doctoc?tab=readme-ov-file#installation)

```
npm install -g doctoc
```

#### Run doctoc
If you modify the README by adding sections, run the following to update the TOC

```
doctoc README.md
```

## Contribution

We warmly welcome and greatly value contributions to the langsmith-evaluation-helper. However, before diving in, we kindly request that you take a moment to review our [Contribution Guidelines](CONTRIBUTING.md).

Additionally, please carefully read the Contributor License Agreement (CLA) before submitting your contribution to Gaudiy. By submitting your contribution, you are considered to have accepted and agreed to be bound by the terms and conditions outlined in the CLA, regardless of circumstances.

https://site.gaudiy.com/contributor-license-agreement
