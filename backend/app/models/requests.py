from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PersonalizeRequest(BaseModel):
    userId: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1, max_length=1000)
    dataSource: Literal["mock", "mongodb"] = "mock"
    llmProvider: Literal["mock", "openrouter", "lmstudio", "openai_compatible"] | None = None
    llmModel: str | None = None

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be blank")
        return value.strip()
