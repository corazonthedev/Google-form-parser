from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class RichTextLine:
    text: str
    styles: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "styles": self.styles or ["normal"]}


@dataclass(slots=True)
class ValidationRule:
    rule: str
    value: str | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {"rule": self.rule}
        if self.value is not None:
            data["value"] = self.value
        if self.message is not None:
            data["message"] = self.message
        return data


@dataclass(slots=True)
class Question:
    title: str
    question_type: str
    required: bool = False
    description: list[RichTextLine] = field(default_factory=list)
    options: list[str] = field(default_factory=list)
    rows: list[str] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    validation: list[ValidationRule] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "title": self.title,
            "type": self.question_type,
            "required": self.required,
        }
        if self.description:
            data["description"] = [line.to_dict() for line in self.description]
        if self.options:
            data["options"] = self.options
        if self.rows:
            data["rows"] = self.rows
        if self.columns:
            data["columns"] = self.columns
        if self.validation:
            data["validation"] = [rule.to_dict() for rule in self.validation]
        return data


@dataclass(slots=True)
class FormPage:
    page_number: int
    section_title: str | None = None
    description: list[RichTextLine] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)
    source_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"page_number": self.page_number}
        if self.section_title:
            data["section_title"] = self.section_title
        if self.description:
            data["description"] = [line.to_dict() for line in self.description]
        data["questions"] = [question.to_dict() for question in self.questions]
        if self.source_path:
            data["source_path"] = self.source_path
        return data


@dataclass(slots=True)
class FormDocument:
    title: str
    source_url: str | None = None
    pages: list[FormPage] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = {"title": self.title, "pages": [page.to_dict() for page in self.pages]}
        if self.source_url:
            data["source_url"] = self.source_url
        return data

    def as_json_ready(self) -> dict[str, Any]:
        return asdict(self)
