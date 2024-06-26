import argparse
import sys


def run() -> None:
    print(sys.argv)

    task_label_help_text = "One or more task labels to run. This is case sensitive."

    choices = ["build", "test"]

    parser = argparse.ArgumentParser(
        description="VS Code Task Runner",
        epilog="When running a single task, extra args can be appended only to that task."
        + " If a single task is requested, but has dependent tasks, only the top-level"
        + " task will be given the extra arguments."
        + ' If the task is a "process" type, then this will be added to "args".'
        + ' If the task is a "shell" type with only a "command" then this will'
        + " be tacked on to the end and joined by spaces."
        + ' If the task is a "shell" type with '
        + ' a "command" and "args", then this will be appended to "args".',
    )
    parser.add_argument(
        "task_labels",
        nargs="+",
        choices=choices,
        help=task_label_help_text,
    )

    args, extra_args = parser.parse_known_args()
    print(args, extra_args)


if __name__ == "__main__":
    run()
