from __future__ import annotations

import json
import re
from pathlib import Path

from .html_parser import GoogleFormHTMLParser
from .models import FormDocument


class FormWorkflowService:
    def __init__(self, parser: GoogleFormHTMLParser | None = None) -> None:
        self.parser = parser or GoogleFormHTMLParser()

    def parse_html_file(self, html_path: str | Path) -> FormDocument:
        path = Path(html_path)
        html = path.read_text(encoding="utf-8")
        page_number = self._page_number_from_name(path.name)
        return self.parser.parse_html(html, page_number=page_number, source_path=str(path))

    def parse_folder(self, folder_path: str | Path) -> FormDocument:
        folder = Path(folder_path)
        pages: list[tuple[int, str, str | None]] = []
        for html_file in sorted(folder.glob("page*.html")):
            pages.append(
                (
                    self._page_number_from_name(html_file.name),
                    html_file.read_text(encoding="utf-8"),
                    str(html_file),
                )
            )
        if not pages:
            raise FileNotFoundError(f"No page*.html files found in {folder}")
        return self.parser.parse_pages(pages)

    def write_json(self, document: FormDocument, output_dir: str | Path) -> Path:
        output_root = Path(output_dir)
        folder_name = self.slugify(document.title)
        target_dir = output_root / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        output_path = target_dir / "parsed_form.json"
        output_path.write_text(
            json.dumps(document.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return output_path

    @staticmethod
    def slugify(value: str) -> str:
        cleaned = value.strip().lower()
        cleaned = cleaned.replace("ı", "i").replace("ğ", "g").replace("ş", "s")
        cleaned = cleaned.replace("ö", "o").replace("ü", "u").replace("ç", "c")
        cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
        cleaned = cleaned.strip("-")
        return cleaned or "untitled-form"

    @staticmethod
    def _page_number_from_name(name: str) -> int:
        match = re.search(r"(\d+)", name)
        return int(match.group(1)) if match else 1
