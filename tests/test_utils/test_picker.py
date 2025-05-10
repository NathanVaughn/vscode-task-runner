import pytest

from vscode_task_runner.exceptions import BadInputEnvironmentVariable
from vscode_task_runner.utils.picker import check_item_with_options


def test_check_item_with_options():
    # check valid option
    env_value = "option1"
    options = ["option1", "option2", "option3"]
    check_item_with_options(env_value, options)

    # check invalid option
    env_value = "invalid_option"
    with pytest.raises(BadInputEnvironmentVariable):
        check_item_with_options(env_value, options)
