from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .workflow import FormWorkflowService


@dataclass(slots=True)
class LiveParseConfig:
    urls: list[str]
    output_dir: str
    email: str | None = None
    password: str | None = None
    headless: bool = True


class SeleniumBaseLiveRunner:
    """Optional live collector. Imported lazily so tests can run without SeleniumBase."""

    NEXT_BUTTON_SELECTOR = "div[jsname='OCpkoe']"
    SUBMIT_BUTTON_SELECTOR = "div[jsname='M2UYVd']"
    LOGIN_EMAIL_SELECTOR = "input[type='email'][autocomplete='username']"
    LOGIN_PASSWORD_SELECTOR = "input[type='password']"

    def __init__(self, workflow: FormWorkflowService | None = None) -> None:
        self.workflow = workflow or FormWorkflowService()

    def run(
        self,
        config: LiveParseConfig,
        *,
        progress: Callable[[str], None] | None = None,
    ) -> list[Path]:
        try:
            from seleniumbase import SB  # type: ignore
        except ImportError as exc:  # pragma: no cover - depends on local machine setup
            raise RuntimeError(
                "seleniumbase is not installed. Install requirements.txt to use live parsing."
            ) from exc

        output_root = Path(config.output_dir)
        output_root.mkdir(parents=True, exist_ok=True)
        written_files: list[Path] = []

        with SB(uc=True, test=True, headless=config.headless) as sb:  # pragma: no cover - e2e only
            for url in config.urls:
                if progress:
                    progress(f"Opening {url}")
                sb.open(url)
                sb.wait_for_ready_state_complete(timeout=20)
                self._maybe_sign_in(sb, config, progress)
                document = self._collect_document(sb, url, progress)
                json_path = self.workflow.write_json(document, output_root)
                if progress:
                    progress(f"Saved {json_path.name}")
                written_files.append(json_path)
        return written_files

    def _collect_document(self, sb, url: str, progress: Callable[[str], None] | None = None):
        pages: list[tuple[int, str, str | None]] = []
        max_pages = 10
        for page_number in range(1, max_pages + 1):
            sb.wait_for_ready_state_complete(timeout=20)
            html = sb.get_page_source()
            pages.append((page_number, html, f"live://page{page_number}"))
            if progress:
                progress(f"Captured page {page_number}")
            if self._is_submit_page(sb):
                break
            advanced = self._advance_to_next_page(sb)
            if not advanced:
                break
        document = self.workflow.parser.parse_pages(pages)
        document.source_url = url
        return document

    def _advance_to_next_page(self, sb) -> bool:
        if not sb.is_element_visible(self.NEXT_BUTTON_SELECTOR):
            return False
        self._fill_visible_fields(sb)
        sb.click(self.NEXT_BUTTON_SELECTOR)
        sb.sleep(1)
        return True

    def _is_submit_page(self, sb) -> bool:
        return sb.is_element_visible(self.SUBMIT_BUTTON_SELECTOR)

    def _maybe_sign_in(
        self,
        sb,
        config: LiveParseConfig,
        progress: Callable[[str], None] | None,
    ) -> None:
        if not config.email or not config.password:
            return
        if not sb.is_element_visible(self.LOGIN_EMAIL_SELECTOR):
            return

        sb.type(self.LOGIN_EMAIL_SELECTOR, config.email)
        if sb.is_element_visible("div[id='identifierNext']"):
            sb.click("div[id='identifierNext']")
        sb.wait_for_ready_state_complete(timeout=20)
        if sb.is_element_visible(self.LOGIN_PASSWORD_SELECTOR):
            sb.type(self.LOGIN_PASSWORD_SELECTOR, config.password)
            if sb.is_element_visible("div[id='passwordNext']"):
                sb.click("div[id='passwordNext']")
            sb.wait_for_ready_state_complete(timeout=20)
        if progress:
            progress("Google sign-in attempted.")

    def _fill_visible_fields(self, sb) -> None:
        script = r"""
        const trigger = (element) => {
          element.dispatchEvent(new Event('input', { bubbles: true }));
          element.dispatchEvent(new Event('change', { bubbles: true }));
          element.dispatchEvent(new Event('blur', { bubbles: true }));
        };

        const visible = (element) => !!(element && element.offsetParent !== null);
        const blocks = [...document.querySelectorAll("form div[jsmodel='CP1oW']")];

        for (const block of blocks) {
          if (!visible(block)) continue;

          const text = block.querySelector("input[type='text']");
          const email = block.querySelector("input[type='email']");
          const url = block.querySelector("input[type='url']");
          const date = block.querySelector("input[type='date']");
          const textarea = block.querySelector("textarea");

          if (text && !text.value) {
            text.value = 'Sample answer';
            trigger(text);
          }
          if (email && !email.value) {
            email.value = 'parser@example.com';
            trigger(email);
          }
          if (url && !url.value) {
            url.value = 'https://example.com';
            trigger(url);
          }
          if (date && !date.value) {
            date.value = '2026-03-25';
            trigger(date);
          }
          if (textarea && !textarea.value) {
            textarea.value = 'Sample answer';
            trigger(textarea);
          }

          const radios = [...block.querySelectorAll("div[role='radio']")]
            .filter(visible);
          if (
            radios.length &&
            !radios.some((node) => node.getAttribute('aria-checked') === 'true')
          ) {
            radios[0].click();
          }

          const checkboxes = [...block.querySelectorAll("div[role='checkbox']")]
            .filter(visible);
          if (
            checkboxes.length &&
            !checkboxes.some((node) => node.getAttribute('aria-checked') === 'true')
          ) {
            checkboxes[0].click();
          }
        }
        """
        sb.execute_script(script)
