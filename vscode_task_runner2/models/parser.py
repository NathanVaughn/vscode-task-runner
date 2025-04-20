from pydantic import BaseModel


class ParseResult(BaseModel):
    task_labels: list[str]
    extra_args: list[str]
