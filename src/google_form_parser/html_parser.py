from __future__ import annotations

import re
from collections.abc import Iterable

from bs4 import BeautifulSoup, Tag

from .models import FormDocument, FormPage, Question, ValidationRule
from .rich_text import extract_rich_text_from_tag

_DESCRIPTION_SELECTORS = [
    "div.cBGGJ.OIC90c",
    "div.vfQisd.Q8wTDd.OIC90c",
]

_SECTION_TITLE_SELECTORS = [
    "div.SajZGc.RVEQke.hN5qnf",
    "div[role='heading'][aria-level='2']",
]

_QUESTION_DESCRIPTION_SELECTORS = [
    "div.gubaDc.OIC90c.RjsPE",
    "div.vfQisd.OIC90c",
]


class GoogleFormHTMLParser:
    """Parses a single Google Form HTML page into structured data."""

    def parse_html(
        self,
        html: str,
        *,
        page_number: int = 1,
        source_path: str | None = None,
        source_url: str | None = None,
    ) -> FormDocument:
        soup = BeautifulSoup(html, "html.parser")
        title = self._form_title(soup)
        page = FormPage(
            page_number=page_number,
            section_title=self._section_title(soup),
            description=self._description(soup),
            questions=self._questions(soup),
            source_path=source_path,
        )
        return FormDocument(title=title, source_url=source_url, pages=[page])

    def _form_title(self, soup: BeautifulSoup) -> str:
        meta = soup.select_one("meta[itemprop='name']")
        if meta and meta.get("content"):
            return self._clean(meta["content"])
        if soup.title and soup.title.text:
            return self._clean(soup.title.text)
        return "Untitled Form"

    def _section_title(self, soup: BeautifulSoup) -> str | None:
        for selector in _SECTION_TITLE_SELECTORS:
            node = soup.select_one(selector)
            if node and self._clean(node.get_text(" ", strip=True)):
                return self._clean(node.get_text(" ", strip=True))
        return None

    def _description(self, soup: BeautifulSoup):
        for selector in _DESCRIPTION_SELECTORS:
            node = soup.select_one(selector)
            if node:
                return extract_rich_text_from_tag(node)
        return []

    def _questions(self, soup: BeautifulSoup) -> list[Question]:
        questions: list[Question] = []
        blocks = soup.select("form div[jsmodel='CP1oW']")
        for block in blocks:
            parsed = self._parse_question(block)
            if parsed:
                questions.append(parsed)
        return questions

    def _parse_question(self, block: Tag) -> Question | None:
        title_node = block.select_one("span.M7eMe") or block.select_one("div[role='heading']")
        if title_node is None:
            return None

        title = self._clean(title_node.get_text(" ", strip=True))
        if not title:
            return None

        required = block.select_one("span.vnumgf") is not None or "*" in title
        description = []
        for selector in _QUESTION_DESCRIPTION_SELECTORS:
            node = block.select_one(selector)
            if node:
                description = extract_rich_text_from_tag(node)
                break

        question_type = self._detect_type(block)
        question = Question(
            title=title,
            question_type=question_type,
            required=required,
            description=description,
        )

        if question_type in {"short_text", "email", "url", "date", "time", "paragraph"}:
            question.validation = self._extract_validation(block)
        elif question_type in {"multiple_choice", "checkbox", "dropdown", "linear_scale"}:
            question.options = self._extract_options(block, question_type)
        elif question_type in {"multiple_choice_grid", "checkbox_grid"}:
            question.rows, question.columns = self._extract_grid(block)
        return question

    def _detect_type(self, block: Tag) -> str:
        if block.select_one("input[type='email']"):
            return "email"
        if block.select_one("input[type='url']"):
            return "url"
        if block.select_one("input[type='date']"):
            return "date"
        if block.select_one("textarea"):
            return "paragraph"
        if block.select_one("div.jscontroller-override-time") or block.select_one("div.IDmXx"):
            return "time"
        if block.select_one("span.l4V7wb.Fxmcue.cd29Sd"):
            return "file_upload"
        if block.select_one("div[jscontroller='FYWcYb']"):
            return "linear_scale"
        if block.select_one("div.gTGYUd"):
            if block.select_one("div.gTGYUd div[role='radiogroup']"):
                return "multiple_choice_grid"
            return "checkbox_grid"
        if block.select_one("div[role='listbox']"):
            return "dropdown"
        if block.select_one("div[jscontroller='UmOCme']"):
            return "multiple_choice"
        if block.select_one("div[jscontroller='sW52Ae']"):
            return "checkbox"
        if block.select_one("input[type='text']"):
            return "short_text"
        return "unknown"

    def _extract_validation(self, block: Tag) -> list[ValidationRule]:
        rules: list[ValidationRule] = []
        input_node = block.select_one("input, textarea")
        if input_node is not None:
            minimum = input_node.get("min")
            maximum = input_node.get("max")
            pattern = input_node.get("pattern")
            if minimum is not None:
                rules.append(ValidationRule(rule="min", value=str(minimum)))
            if maximum is not None:
                rules.append(ValidationRule(rule="max", value=str(maximum)))
            if pattern:
                rules.append(ValidationRule(rule="pattern", value=pattern))

        helper_text = self._helper_text(block)
        if helper_text:
            rules.append(ValidationRule(rule="helper_text", message=helper_text))
        return rules

    def _extract_options(self, block: Tag, question_type: str) -> list[str]:
        selectors = {
            "multiple_choice": [
                "div[jscontroller='UmOCme'] span.aDTYNe.snByac.OvPDhc.OIC90c",
                "div[jscontroller='UmOCme'] label span",
            ],
            "checkbox": [
                "div[jscontroller='sW52Ae'] span.aDTYNe.snByac.n5vBHf.OIC90c",
                "div[jscontroller='sW52Ae'] label span",
            ],
            "dropdown": [
                "div[role='listbox'] span.vRMGwf.oJeWuf",
                "div[role='option'] span",
            ],
            "linear_scale": [
                "div[jscontroller='FYWcYb'] div.Zki2Ve",
                "div[jscontroller='FYWcYb'] label",
            ],
        }

        values: list[str] = []
        for selector in selectors.get(question_type, []):
            for node in block.select(selector):
                text = self._clean(node.get_text(" ", strip=True))
                if text:
                    values.append(text)
            if values:
                break
        return list(dict.fromkeys(values))

    def _extract_grid(self, block: Tag) -> tuple[list[str], list[str]]:
        columns = [
            self._clean(node.get_text(" ", strip=True))
            for node in block.select("div.ssX1Bd.KZt9Tc div.V4d7Ke.OIC90c")
            if self._clean(node.get_text(" ", strip=True))
        ]
        deduplicated_columns = (
            columns[: len(columns) // 2]
            if columns[len(columns) // 2 :] == columns[: len(columns) // 2]
            else columns
        )
        rows = [
            self._clean(node.get_text(" ", strip=True))
            for node in block.select("div.lLfZXe.fnxRtf.EzyPc")
            if self._clean(node.get_text(" ", strip=True))
        ]
        return rows, deduplicated_columns

    def _helper_text(self, block: Tag) -> str | None:
        candidates = [
            "span.RHiWt",
            "div[role='alert']",
            "div.vfQisd[aria-live='polite']",
        ]
        for selector in candidates:
            node = block.select_one(selector)
            if node:
                text = self._clean(node.get_text(" ", strip=True))
                if text:
                    return text
        return None

    def _clean(self, value: str) -> str:
        return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()

    def parse_pages(self, pages: Iterable[tuple[int, str, str | None]]) -> FormDocument:
        parsed_pages: list[FormPage] = []
        title = "Untitled Form"
        source_url = None
        for page_number, html, source_path in sorted(pages, key=lambda item: item[0]):
            document = self.parse_html(
                html,
                page_number=page_number,
                source_path=source_path,
                source_url=source_url,
            )
            title = document.title
            source_url = document.source_url
            parsed_pages.extend(document.pages)
        return FormDocument(title=title, source_url=source_url, pages=parsed_pages)
