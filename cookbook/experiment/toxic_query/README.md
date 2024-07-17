# Evaluate an LLM Application

In this case, we are defining a simple evaluation target consisting of an 
LLM pipeline that classifies text as toxic or non-toxic.

# config_basic.yml
Basic example with a single provider

Note: Run [toxic_query_dataset.py](/cookbook/setup) once in advance to set-up the dataset in LangSmith.

# config_assert.yml
Here we specify validation criteria for test results using [assert types](/README.md#tests).	

Note: Run [toxic_query_dataset.py](/cookbook/setup) once in advance to set-up the dataset in LangSmith.

# config_limit.yml
Here we limit the number of runs for the experiment [limit](/README.md#tests).

Note: Run [toxic_query_dataset.py](/cookbook/setup) once in advance to set-up the dataset in LangSmith.

# config_multi_provider.yml
Here we also run the experiments with two [providers](/README.md#providers).

Check the link in the output for a comparison between the results of the 
experiments with the two providers. The view should look like [this](https://docs.smith.langchain.com/how_to_guides/evaluation/compare_experiment_results).

Note: Run [toxic_query_dataset.py](/cookbook/setup) once in advance to set-up the dataset in LangSmith.

# config_split.yml
We also split the dataset during creation.
Check out the [official Langsmith docs](https://docs.smith.langchain.com/how_to_guides/datasets/manage_datasets_in_application#create-and-manage-dataset-splits) for more details.

Here we run the experiments on a specific [split](/README.md#tests).

Note: Run [toxic_query_split_dataset.py](/cookbook/setup/toxic_query_split_dataset.py) once in advance to set-up the dataset in LangSmith.

# config_custom_run.yml
We are able to run any function(chain, graph, RAG, etc.) with `custom run`.

Note: Run [toxic_query_dataset.py](/cookbook/setup) once in advance to set-up the dataset in LangSmith.
