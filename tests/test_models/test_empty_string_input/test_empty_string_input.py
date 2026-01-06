import os

from tests.conftest import tasks_obj


def test_empty_string_input() -> None:
    """Test that empty string pickString options work correctly."""
    # Set environment variable to automatically select the empty string option
    os.environ["VTR_INPUT_testInput"] = ""

    try:
        tasks = tasks_obj(__file__)

        # Verify that the tasks were loaded successfully
        assert tasks is not None
        assert "task1" in tasks.tasks_dict

        task = tasks.tasks_dict["task1"]
        # The task should have been created successfully with empty string input
        assert task is not None
    finally:
        # Clean up the environment variable
        if "VTR_INPUT_testInput" in os.environ:
            del os.environ["VTR_INPUT_testInput"]
