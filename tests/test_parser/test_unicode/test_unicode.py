from tests.conftest import tasks_obj


def test_unicode_parsing() -> None:
    # make sure it parses with no errors
    tasks_obj(__file__)
