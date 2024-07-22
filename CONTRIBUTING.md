# Contribution Guidelines

Thank you for considering contributing to this repository! We appreciate your support and efforts to improve the project. Below are the guidelines to help you get started with contributing.

## How to Contribute

1. **Fork the repository**: Click on the "Fork" button at the top right corner of the repository page to create a copy of the repository in your GitHub account.

2. **Clone the repository**: Clone the forked repository to your local machine using the following command:
   ```bash
   git clone https://github.com/your-username/repository-name.git
   ```

3. **Create a new branch**: Create a new branch for your contribution using the following command:
   ```bash
   git checkout -b your-branch-name
   ```

4. **Make your changes**: Make the necessary changes to the codebase. Ensure that your changes adhere to the coding standards and best practices mentioned below.

5. **Commit your changes**: Commit your changes with a descriptive commit message using the following command:
   ```bash
   git commit -m "Description of your changes"
   ```

6. **Push your changes**: Push your changes to your forked repository using the following command:
   ```bash
   git push origin your-branch-name
   ```

7. **Create a pull request**: Go to the original repository on GitHub and create a pull request from your forked repository. Provide a clear and concise description of your changes in the pull request.

## Setting Up the Development Environment

If you have not installed uv, install as following:

```
# With pip
pip install uv

# With Homebrew.
brew install uv
```

To set up the development environment, follow these steps:

1. **Create a virtual environment**: Create a virtual environment using the following command:
   ```bash
   uv venv --python=$(which python3.10)
   ```

2. **Activate the virtual environment**: Activate the virtual environment using the following command:
   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies**: Install the required dependencies using the following command:
   ```bash
   uv pip sync requirements.txt
   ```

4. **Install the package locally**: Install the package in editable mode using the following command:
   ```bash
   uv pip install -e .
   ```

5. **Set up environment variables**: Create a `.env` file in the root of the repository and add the necessary environment variables. For example:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   AZURE_OPENAI_API_BASE=your_azure_openai_api_base
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

6. **Run tests**: Run the tests to ensure that your changes do not introduce any new issues. Use the following command:
   ```bash
   make test
   ```

## Coding Standards and Best Practices

- Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) coding style guide for Python code.
- Write clear and concise comments to explain the purpose of your code.
- Ensure that your code is well-documented and includes docstrings for functions and classes.
- Write unit tests for your code to ensure its correctness and reliability.
- Use meaningful variable and function names that accurately describe their purpose.
- Avoid using magic numbers and hard-coded values. Use constants or configuration files instead.
- Keep your code modular and follow the single responsibility principle.

## Submitting Pull Requests

When submitting a pull request, please ensure the following:

- Your pull request has a clear and descriptive title.
- Your pull request includes a detailed description of the changes you have made.
- Your pull request is based on the latest version of the main branch.
- Your pull request includes any necessary documentation updates.
- Your pull request passes all the tests and does not introduce any new issues.

Thank you for your contributions! We appreciate your efforts to make this project better.
