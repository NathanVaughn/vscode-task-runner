"""Test --list-inputs functionality."""

import sys
from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch


from vscode_task_runner.console import run


def test_list_inputs_single_task(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]):
    """
    Test --list-inputs with a single task
    """
    # Change to test directory
    test_dir = Path(__file__).parent
    monkeypatch.chdir(test_dir)

    # Mock sys.argv
    monkeypatch.setattr(sys, "argv", ["vtr", "deploy", "--list-inputs"])

    # Run the command
    exit_code = run()

    # Should exit successfully
    assert exit_code == 0

    # Capture output
    captured = capsys.readouterr()

    # Check that input information is displayed
    assert "environment" in captured.out
    assert "region" in captured.out
    assert "pickString" in captured.out
    assert "Deployment environment" in captured.out
    assert "AWS region" in captured.out
    assert "--input-environment=" in captured.out
    assert "--input-region=" in captured.out


def test_list_inputs_with_dependencies(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
):
    """
    Test --list-inputs with a task that has dependencies
    """
    test_dir = Path(__file__).parent
    monkeypatch.chdir(test_dir)

    # Mock sys.argv - deploy-with-deps depends on both build and deploy
    monkeypatch.setattr(sys, "argv", ["vtr", "deploy-with-deps", "--list-inputs"])

    # Run the command
    exit_code = run()

    # Should exit successfully
    assert exit_code == 0

    # Capture output
    captured = capsys.readouterr()

    # Should show inputs from all dependent tasks
    assert "environment" in captured.out
    assert "region" in captured.out
    assert "build_type" in captured.out


def test_list_inputs_multiple_tasks(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
):
    """
    Test --list-inputs with multiple tasks
    """
    test_dir = Path(__file__).parent
    monkeypatch.chdir(test_dir)

    # Mock sys.argv - specify both deploy and build
    monkeypatch.setattr(sys, "argv", ["vtr", "deploy", "build", "--list-inputs"])

    # Run the command
    exit_code = run()

    # Should exit successfully
    assert exit_code == 0

    # Capture output
    captured = capsys.readouterr()

    # Should show inputs from both tasks
    assert "environment" in captured.out
    assert "region" in captured.out
    assert "build_type" in captured.out


def test_list_inputs_with_options_display(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
):
    """
    Test that --list-inputs displays options for pickString inputs
    """
    test_dir = Path(__file__).parent
    monkeypatch.chdir(test_dir)

    # Mock sys.argv
    monkeypatch.setattr(sys, "argv", ["vtr", "deploy", "--list-inputs"])

    # Run the command
    exit_code = run()

    # Should exit successfully
    assert exit_code == 0

    # Capture output
    captured = capsys.readouterr()

    # Check that options are displayed
    assert "dev" in captured.out
    assert "staging" in captured.out
    assert "production" in captured.out
    assert "us-west-2" in captured.out or "US West (Oregon)" in captured.out
    assert "us-east-1" in captured.out or "US East (Virginia)" in captured.out


def test_list_inputs_does_not_execute_task(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
):
    """
    Test that --list-inputs does not execute the task
    """
    test_dir = Path(__file__).parent
    monkeypatch.chdir(test_dir)

    # Mock sys.argv
    monkeypatch.setattr(sys, "argv", ["vtr", "deploy", "--list-inputs"])

    # Run the command
    exit_code = run()

    # Should exit successfully
    assert exit_code == 0

    # Capture output
    captured = capsys.readouterr()

    # Should NOT contain task execution output
    assert "Deploying to" not in captured.out
    assert "Executing task" not in captured.out
