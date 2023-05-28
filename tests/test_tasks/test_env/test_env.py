from tests.conftest import load_task


def test_env(linux: None) -> None:
    task = load_task(__file__, "Test")
    assert task.env["KEY1"] == "VALUE1"
    assert task.env["PATH"] == "PATHOVERRIDE"
    assert len(task.env.keys()) > 2
