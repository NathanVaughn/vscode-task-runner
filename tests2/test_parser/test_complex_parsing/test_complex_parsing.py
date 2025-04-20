from tests2.conftest import tasks_obj


def test_parsing() -> None:
    # make sure it parses with no errors
    tasks_obj(__file__)
