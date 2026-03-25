import json
from pathlib import Path

from google_form_parser.workflow import FormWorkflowService

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_folder_merges_pages_in_order(tmp_path: Path) -> None:
    folder = tmp_path / "source"
    folder.mkdir()
    (folder / "page2.html").write_text(
        (FIXTURES / "simple_form_page2.html").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (folder / "page1.html").write_text(
        (FIXTURES / "simple_form_page1.html").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    workflow = FormWorkflowService()
    document = workflow.parse_folder(folder)

    assert document.title == "Customer Intake Form"
    assert [page.page_number for page in document.pages] == [1, 2]
    assert document.pages[1].section_title == "Preferences"


def test_write_json_creates_slugged_output(tmp_path: Path) -> None:
    workflow = FormWorkflowService()
    document = workflow.parse_html_file(FIXTURES / "simple_form_page1.html")

    output_path = workflow.write_json(document, tmp_path)

    assert output_path.name == "parsed_form.json"
    assert output_path.parent.name == "customer-intake-form"
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["title"] == "Customer Intake Form"
    assert payload["pages"][0]["questions"][0]["title"] == "Full name"


def test_slugify_handles_turkish_characters() -> None:
    assert FormWorkflowService.slugify("Özel Şirket Formu") == "ozel-sirket-formu"
