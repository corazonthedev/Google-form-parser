from pathlib import Path

from google_form_parser.cli import main


def test_cli_writes_output_for_single_html_file(monkeypatch, tmp_path: Path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "simple_form_page1.html"
    output_dir = tmp_path / "out"
    monkeypatch.setattr(
        "sys.argv",
        [
            "google-form-parser",
            "--html-file",
            str(fixture),
            "--output-dir",
            str(output_dir),
        ],
    )

    exit_code = main()

    assert exit_code == 0
    json_files = list(output_dir.glob("**/parsed_form.json"))
    assert len(json_files) == 1
