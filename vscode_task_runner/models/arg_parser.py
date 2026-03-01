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
    input_values: dict[str, str] = {}
    """
    Input values provided via --input-<id>=<value> CLI flags
    """
    list_inputs: bool = False
    """
    Whether to list inputs and exit
    """
