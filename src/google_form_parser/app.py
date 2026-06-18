from __future__ import annotations

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .live_runner import LiveParseConfig, SeleniumBaseLiveRunner
from .workflow import FormWorkflowService


class GoogleFormParserApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Google Form Parser")
        self.root.geometry("920x680")
        self.root.minsize(820, 620)

        self.workflow = FormWorkflowService()
        self.live_runner = SeleniumBaseLiveRunner(self.workflow)

        self.urls_var = tk.StringVar()
        self.email_var = tk.StringVar(value=os.getenv("GOOGLE_FORM_EMAIL", ""))
        self.password_var = tk.StringVar(value=os.getenv("GOOGLE_FORM_PASSWORD", ""))
        self.output_dir_var = tk.StringVar(value=os.getenv("GOOGLE_FORM_OUTPUT_DIR", "./FORMS"))
        self.saved_html_var = tk.StringVar()
        self.headless_var = tk.BooleanVar(
            value=os.getenv("GOOGLE_FORM_HEADLESS", "true").lower() == "true"
        )
        self.status_var = tk.StringVar(value="Ready")

        self._build()

    def run(self) -> None:
        self.root.mainloop()

    def _build(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        shell = ttk.Frame(self.root, padding=18)
        shell.grid(sticky="nsew")
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(2, weight=1)

        header = ttk.Frame(shell)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Google Form Parser", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text=(
                "Original desktop flow korunuyor; güvenlik, yapı ve okunabilirlik "
                "geliştirildi."
            ),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        summary = ttk.LabelFrame(shell, text="Quick notes", padding=12)
        summary.grid(row=1, column=0, sticky="ew", pady=(16, 12))
        summary.columnconfigure(0, weight=1)
        ttk.Label(
            summary,
            text=(
                "• Live parse: URL açılır, HTML okunur, JSON yazılır.\n"
                "• Saved HTML: page1.html, page2.html gibi dosyalardan da parse eder.\n"
                "• Şifre kaydedilmez; sadece bu oturum için bellekte tutulur."
            ),
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        notebook = ttk.Notebook(shell)
        notebook.grid(row=2, column=0, sticky="nsew")

        live_tab = ttk.Frame(notebook, padding=16)
        html_tab = ttk.Frame(notebook, padding=16)
        notebook.add(live_tab, text="Live form URL")
        notebook.add(html_tab, text="Saved HTML")

        self._build_live_tab(live_tab)
        self._build_html_tab(html_tab)

        console = ttk.LabelFrame(shell, text="Status", padding=12)
        console.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        console.columnconfigure(0, weight=1)
        console.rowconfigure(0, weight=1)

        self.log_box = tk.Text(console, height=10, wrap="word", state="disabled")
        self.log_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(shell, textvariable=self.status_var).grid(
            row=4,
            column=0,
            sticky="w",
            pady=(8, 0),
        )

    def _build_live_tab(self, tab: ttk.Frame) -> None:
        tab.columnconfigure(1, weight=1)
        ttk.Label(tab, text="Form URLs (one per line)").grid(row=0, column=0, sticky="w")
        urls = tk.Text(tab, height=8, wrap="word")
        urls.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(6, 12))
        tab.rowconfigure(1, weight=1, minsize=40)
        ttk.Sizegrip(tab).grid(row=1, column=2, sticky="se")

        def sync_urls(*_: object) -> None:
            self.urls_var.set(urls.get("1.0", "end").strip())

        urls.bind("<KeyRelease>", sync_urls)

        ttk.Label(tab, text="Email (optional)").grid(row=2, column=0, sticky="w")
        ttk.Entry(tab, textvariable=self.email_var).grid(row=2, column=1, sticky="ew", padx=(10, 0))

        ttk.Label(tab, text="Password (optional)").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(tab, textvariable=self.password_var, show="•").grid(
            row=3,
            column=1,
            sticky="ew",
            padx=(10, 0),
            pady=(10, 0),
        )

        ttk.Label(tab, text="Output folder").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(tab, textvariable=self.output_dir_var).grid(
            row=4,
            column=1,
            sticky="ew",
            padx=(10, 0),
            pady=(10, 0),
        )
        ttk.Button(tab, text="Browse", command=self._choose_output_dir).grid(
            row=4,
            column=2,
            sticky="ew",
            padx=(10, 0),
            pady=(10, 0),
        )

        ttk.Checkbutton(tab, text="Run headless", variable=self.headless_var).grid(
            row=5,
            column=0,
            sticky="w",
            pady=(12, 0),
        )
        ttk.Button(tab, text="Parse live URLs", command=self._parse_live).grid(
            row=5,
            column=2,
            sticky="e",
            pady=(12, 0),
        )

    def _build_html_tab(self, tab: ttk.Frame) -> None:
        tab.columnconfigure(1, weight=1)
        ttk.Label(tab, text="Folder containing page*.html files").grid(
            row=0,
            column=0,
            sticky="w",
        )
        ttk.Entry(tab, textvariable=self.saved_html_var).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(10, 0),
        )
        ttk.Button(tab, text="Browse", command=self._choose_html_dir).grid(
            row=0,
            column=2,
            sticky="ew",
            padx=(10, 0),
        )

        ttk.Label(tab, text="Output folder").grid(row=1, column=0, sticky="w", pady=(12, 0))
        ttk.Entry(tab, textvariable=self.output_dir_var).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(10, 0),
            pady=(12, 0),
        )
        ttk.Button(tab, text="Browse", command=self._choose_output_dir).grid(
            row=1,
            column=2,
            sticky="ew",
            padx=(10, 0),
            pady=(12, 0),
        )

        ttk.Button(tab, text="Parse saved HTML", command=self._parse_saved_html).grid(
            row=2,
            column=2,
            sticky="e",
            pady=(16, 0),
        )

    def _choose_output_dir(self) -> None:
        selected = filedialog.askdirectory()
        if selected:
            self.output_dir_var.set(selected)

    def _choose_html_dir(self) -> None:
        selected = filedialog.askdirectory()
        if selected:
            self.saved_html_var.set(selected)

    def _append_log(self, text: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{text}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.status_var.set(text)

    def _parse_saved_html(self) -> None:
        folder = self.saved_html_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        if not folder:
            messagebox.showerror(
                "Missing folder",
                "Select the folder that contains page*.html files.",
            )
            return

        try:
            document = self.workflow.parse_folder(folder)
            output_path = self.workflow.write_json(document, output_dir)
            self._append_log(f"Saved JSON to {output_path}")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Parse failed", str(exc))
            self._append_log(f"Error: {exc}")

    def _parse_live(self) -> None:
        urls = [line.strip() for line in self.urls_var.get().splitlines() if line.strip()]
        if not urls:
            messagebox.showerror("Missing URL", "Paste at least one Google Form URL.")
            return

        output_dir = self.output_dir_var.get().strip() or "./FORMS"
        config = LiveParseConfig(
            urls=urls,
            output_dir=output_dir,
            email=self.email_var.get().strip() or None,
            password=self.password_var.get() or None,
            headless=self.headless_var.get(),
        )
        worker = threading.Thread(target=self._run_live_thread, args=(config,), daemon=True)
        worker.start()

    def _run_live_thread(self, config: LiveParseConfig) -> None:
        def progress(message: str) -> None:
            self.root.after(0, lambda: self._append_log(message))

        try:
            files = self.live_runner.run(config, progress=progress)
            self.root.after(0, lambda: self._append_log(f"Completed {len(files)} form(s)."))
        except Exception as exc:  # noqa: BLE001
            error_message = str(exc)
            self.root.after(
                0,
                lambda message=error_message: messagebox.showerror(
                    "Live parse failed",
                    message,
                ),
            )
            self.root.after(0, lambda message=error_message: self._append_log(f"Error: {message}"))


def launch() -> None:
    Path("FORMS").mkdir(exist_ok=True)
    app = GoogleFormParserApp()
    app.run()
