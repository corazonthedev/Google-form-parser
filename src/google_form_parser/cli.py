from __future__ import annotations

import argparse
from pathlib import Path

from .workflow import FormWorkflowService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse Google Form HTML into JSON.")
    parser.add_argument("--html-folder", help="Folder containing page*.html files")
    parser.add_argument("--html-file", help="Single HTML file to parse")
    parser.add_argument("--output-dir", default="./FORMS", help="Output directory for JSON files")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    workflow = FormWorkflowService()

    if args.html_folder:
        document = workflow.parse_folder(args.html_folder)
    elif args.html_file:
        document = workflow.parse_html_file(args.html_file)
    else:
        parser.error("Provide --html-folder or --html-file")

    output_path = workflow.write_json(document, Path(args.output_dir))
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
