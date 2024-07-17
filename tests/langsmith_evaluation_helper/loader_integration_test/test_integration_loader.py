import subprocess
import pytest


@pytest.mark.integration_test
def test_loader():
    # Run the loader.py script and capture the output
    result = subprocess.run(
        [
            "langsmith-evaluation-helper",
            "evaluate",
            "tests/langsmith_evaluation_helper/loader_integration_test/config_basic.yml",
        ],
        capture_output=True,
        text=True,
    )

    # Print the captured output
    print(result.stdout)
    print(result.stderr)

    # Assert that the script executed without errors
    assert result.returncode == 0
    assert "error" not in result.stderr.lower()
