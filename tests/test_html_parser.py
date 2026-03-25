from pathlib import Path

from google_form_parser.html_parser import GoogleFormHTMLParser

FIXTURES = Path(__file__).parent / "fixtures"


def _read(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_simple_page_extracts_title_description_and_questions() -> None:
    parser = GoogleFormHTMLParser()

    document = parser.parse_html(_read("simple_form_page1.html"), page_number=1)

    assert document.title == "Customer Intake Form"
    assert len(document.pages) == 1
    page = document.pages[0]
    assert page.page_number == 1
    assert [line.text for line in page.description] == ["Welcome", "team", "help"]
    assert page.questions[0].title == "Full name"
    assert page.questions[0].required is True
    assert page.questions[0].question_type == "short_text"
    assert {rule.rule for rule in page.questions[0].validation} >= {"min", "max"}
    assert page.questions[2].question_type == "paragraph"


def test_parse_second_page_extracts_section_title_and_choice_options() -> None:
    parser = GoogleFormHTMLParser()

    document = parser.parse_html(_read("simple_form_page2.html"), page_number=2)

    page = document.pages[0]
    assert page.section_title == "Preferences"
    assert page.questions[0].question_type == "multiple_choice"
    assert page.questions[0].options == ["Starter", "Growth", "Enterprise"]
    assert page.questions[1].question_type == "checkbox"
    assert page.questions[1].options == ["Monday", "Wednesday"]


def test_parse_advanced_question_types() -> None:
    parser = GoogleFormHTMLParser()

    document = parser.parse_html(_read("question_types.html"), page_number=1)
    questions = {question.title: question for question in document.pages[0].questions}

    assert questions["Email"].question_type == "email"
    assert questions["Meeting time"].question_type == "time"
    assert questions["Launch date"].question_type == "date"
    assert questions["Priority"].options == ["Low", "High"]
    assert questions["Satisfaction"].options == ["1", "2", "3"]
    assert questions["Department ratings"].question_type == "multiple_choice_grid"
    assert questions["Department ratings"].rows == ["Support", "Sales"]
    assert questions["Department ratings"].columns == ["Bad", "Good"]
    assert questions["Attachment"].question_type == "file_upload"
