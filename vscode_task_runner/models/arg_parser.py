from pydantic import BaseModel


class ArgParseResult(BaseModel):
    task_labels: list[str]
    """
    Selected task labels
    """
    extra_args: list[str]
    """
    Extra arguments provided
    """
