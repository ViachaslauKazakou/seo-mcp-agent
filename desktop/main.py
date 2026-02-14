import sys
from typing import Any, Dict, List

import httpx
from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


API_BASE_URL = "http://127.0.0.1:8030"


class AnalyzeWorker(QObject):
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, payload: Dict[str, Any], parent: QObject | None = None):
        super().__init__(parent)
        self.payload = payload

    def run(self) -> None:
        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(f"{API_BASE_URL}/api/analyze", json=self.payload)
                response.raise_for_status()
                self.finished.emit(response.json())
        except Exception as exc:  # pragma: no cover - UI error path
            self.failed.emit(str(exc))


class SeoMcpAgent(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.worker_thread: QThread | None = None
        self.worker: AnalyzeWorker | None = None
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle("SEO Agent - Desktop")
        self.resize(900, 700)

        self.setStyleSheet(
            ""
            "QWidget {"
            "  background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            "    stop:0 #667eea, stop:1 #764ba2);"
            "  font-family: -apple-system, 'Segoe UI', Roboto, sans-serif;"
            "}"
            "QFrame#Card {"
            "  background: white;"
            "  border-radius: 12px;"
            "}"
            "QPushButton#PrimaryButton {"
            "  background: #3377ee;"
            "  color: black;"
            "  border-radius: 8px;"
            "  padding: 10px;"
            "  font-weight: bold;"
            "}"
            "QPushButton#PrimaryButton:disabled {"
            "  background: #a0a7ea;"
            "}"
            "QLabel#Subtitle { color: #666; font-size: 13px; }"
            "QFrame#StatCard {"
            "  border-left: 4px solid #667eea;"
            "  background: #f8f9ff;"
            "  border-radius: 8px;"
            "}"
            "QFrame#AlertInfo {"
            "  border-left: 4px solid #667eea;"
            "  background: #eef2ff;"
            "  border-radius: 8px;"
            "}"
            "QFrame#AlertSuccess {"
            "  border-left: 4px solid #16a34a;"
            "  background: #ecfdf3;"
            "  border-radius: 8px;"
            "}"
            "QFrame#AlertError {"
            "  border-left: 4px solid #dc2626;"
            "  background: #fef2f2;"
            "  border-radius: 8px;"
            "}"
            "QFrame#ListItem {"
            "  background: #ffffff;"
            "  border: 1px solid #e5e7eb;"
            "  border-radius: 8px;"
            "}"
            ""
        )

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(0)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

        title = QLabel("🔍 SEO Agent")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Arial", 20, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: black;")
        card_layout.addWidget(title)

        subtitle = QLabel("Analyze your website for SEO opportunities")
        subtitle.setObjectName("Subtitle")
        card_layout.addWidget(subtitle)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.setMinimumHeight(40)
        card_layout.addWidget(self.url_input)
        fetcher_label = QLabel("🔗 Content Parser")
        fetcher_label.setStyleSheet("color: #333; font-weight: bold;")
        card_layout.addWidget(fetcher_label)

        fetcher_row = QHBoxLayout()
        self.fetcher_group = QButtonGroup(self)
        self.fetcher_httpx = QRadioButton("⚡ Standard (httpx) - Fast")
        self.fetcher_playwright = QRadioButton("🎭 PlayWright - JavaScript")
        self.fetcher_httpx.setChecked(True)
        self.fetcher_group.addButton(self.fetcher_httpx)
        self.fetcher_group.addButton(self.fetcher_playwright)
        fetcher_row.addWidget(self.fetcher_httpx)
        fetcher_row.addWidget(self.fetcher_playwright)
        fetcher_row.addStretch(1)
        card_layout.addLayout(fetcher_row)
        provider_label = QLabel("📊 Embedding Provider")
        provider_label.setStyleSheet("color: black; font-weight: bold;")
        card_layout.addWidget(provider_label)

        provider_row = QHBoxLayout()
        self.provider_group = QButtonGroup(self)
        self.provider_hf = QRadioButton("🤗 HuggingFace")
        self.provider_openai = QRadioButton("🔑 OpenAI")
        self.provider_hf.setChecked(True)
        self.provider_group.addButton(self.provider_hf)
        self.provider_group.addButton(self.provider_openai)
        provider_row.addWidget(self.provider_hf)
        provider_row.addWidget(self.provider_openai)
        provider_row.addStretch(1)
        card_layout.addLayout(provider_row)

        self.openai_embedding_row = QHBoxLayout()
        openai_label = QLabel("OpenAI Embedding Model")
        openai_label.setStyleSheet("color: black; font-weight: bold;")
        self.openai_embedding_select = QComboBox()
        self.openai_embedding_select.addItems(
            ["text-embedding-3-small", "text-embedding-3-large"]
        )
        self.openai_embedding_row.addWidget(openai_label)
        self.openai_embedding_row.addWidget(self.openai_embedding_select)
        card_layout.addLayout(self.openai_embedding_row)

        self.use_openai_checkbox = QCheckBox(
            "Use OpenAI for AI-powered recommendations (requires OPENAI_API_KEY)"
        )
        card_layout.addWidget(self.use_openai_checkbox)

        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setObjectName("PrimaryButton")
        self.analyze_button.setMinimumHeight(44)
        self.analyze_button.clicked.connect(self.start_analysis)
        card_layout.addWidget(self.analyze_button)

        self.result_frame = QFrame()
        self.result_frame.setObjectName("AlertInfo")
        self.result_frame.setVisible(False)
        result_layout = QVBoxLayout(self.result_frame)
        result_layout.setContentsMargins(16, 16, 16, 16)
        result_layout.setSpacing(12)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-weight: bold; color: black;")
        result_layout.addWidget(self.status_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setSpacing(12)
        self.results_layout.addStretch(1)
        self.scroll_area.setWidget(self.results_container)
        result_layout.addWidget(self.scroll_area)

        card_layout.addWidget(self.result_frame)

        outer_layout.addWidget(card)

        self.provider_openai.toggled.connect(self.update_provider_ui)
        self.update_provider_ui()

    def update_provider_ui(self) -> None:
        is_openai = self.provider_openai.isChecked()
        for i in range(self.openai_embedding_row.count()):
            widget = self.openai_embedding_row.itemAt(i).widget()
            if widget is not None:
                widget.setVisible(is_openai)

    def start_analysis(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            self.show_error("Please enter a URL.")
            return
        if not (url.startswith("http://") or url.startswith("https://")):
            self.show_error("URL must start with http:// or https://")
            return

        fetcher = "playwright" if self.fetcher_playwright.isChecked() else "httpx"
        provider = "openai" if self.provider_openai.isChecked() else "hf"
        payload = {
            "urls": [url],
            "fetcher_type": fetcher,
            "use_openai": self.use_openai_checkbox.isChecked(),
            "embedding_provider": provider,
            "openai_embedding_model": self.openai_embedding_select.currentText(),
        }

        self.analyze_button.setEnabled(False)
        self.result_frame.setVisible(True)
        self.result_frame.setObjectName("AlertInfo")
        self.result_frame.setStyleSheet("")
        self.status_label.setText("⏳ Analyzing...")
        self.clear_results()

        self.worker_thread = QThread(self)
        self.worker = AnalyzeWorker(payload)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_analysis_success)
        self.worker.failed.connect(self.on_analysis_error)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def on_analysis_success(self, data: Dict[str, Any]) -> None:
        self.analyze_button.setEnabled(True)
        self.result_frame.setObjectName("AlertSuccess")
        self.result_frame.setStyleSheet("")
        self.status_label.setText("✅ Analysis completed")
        self.render_results(data)

    def on_analysis_error(self, message: str) -> None:
        self.analyze_button.setEnabled(True)
        self.result_frame.setObjectName("AlertError")
        self.result_frame.setStyleSheet("")
        self.status_label.setText(f"❌ Error: {message}")

    def show_error(self, message: str) -> None:
        self.result_frame.setVisible(True)
        self.result_frame.setObjectName("AlertError")
        self.result_frame.setStyleSheet("")
        self.status_label.setText(f"❌ {message}")
        self.clear_results()

    def clear_results(self) -> None:
        while self.results_layout.count() > 1:
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def render_results(self, data: Dict[str, Any]) -> None:
        self.clear_results()

        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)
        stats_layout.setSpacing(12)

        stats = [
            ("Documents Parsed", data.get("documents_parsed", 0)),
            ("Keywords Found", len(data.get("keywords_extracted", []))),
            ("Clusters", len(data.get("clusters", []))),
            ("Recommendations", len(data.get("recommendations", []))),
        ]
        for idx, (label, value) in enumerate(stats):
            card = self.create_stat_card(label, str(value))
            stats_layout.addWidget(card, idx // 2, idx % 2)

        self.results_layout.insertWidget(0, stats_widget)

        intent_summary = data.get("intent_summary", {})
        if not intent_summary and data.get("keywords_extracted"):
            for kw in data.get("keywords_extracted", []):
                intent = kw.get("intent") or "informational"
                intent_summary[intent] = intent_summary.get(intent, 0) + 1
        if intent_summary:
            self.results_layout.insertWidget(
                1, self.create_section_title("Intent Breakdown")
            )
            for intent, count in intent_summary.items():
                item = self.create_list_item(intent, str(count))
                self.results_layout.insertWidget(self.results_layout.count() - 1, item)

        keywords = data.get("keywords_extracted", [])[:10]
        if keywords:
            self.results_layout.insertWidget(1, self.create_section_title("Top Keywords"))
            for kw in keywords:
                intent = kw.get("intent")
                title = kw.get("keyword", "")
                if intent:
                    title = f"{title} ({intent})"
                item = self.create_list_item(
                    title,
                    f"{kw.get('tf_idf_score', 0.0):.3f}",
                )
                self.results_layout.insertWidget(self.results_layout.count() - 1, item)

        recommendations = data.get("recommendations", [])
        if recommendations:
            self.results_layout.insertWidget(self.results_layout.count() - 1, self.create_section_title("Recommendations"))
            for rec in recommendations:
                title = rec.get("title", "")
                description = rec.get("description", "")
                priority = rec.get("priority", 1)
                source = rec.get("evidence", {}).get("source")
                badge = f"{priority}/5"
                if source == "openai":
                    title = f"{title} (AI)"
                item = self.create_list_item(title, badge, description)
                self.results_layout.insertWidget(self.results_layout.count() - 1, item)

        errors = data.get("errors", [])
        if errors:
            error_frame = QFrame()
            error_frame.setObjectName("AlertError")
            error_layout = QVBoxLayout(error_frame)
            error_layout.setContentsMargins(12, 12, 12, 12)
            error_layout.addWidget(QLabel("⚠️ Errors"))
            for err in errors:
                error_layout.addWidget(QLabel(f"• {err}"))
            self.results_layout.insertWidget(self.results_layout.count() - 1, error_frame)

    def create_stat_card(self, label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("StatCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        label_widget = QLabel(label)
        label_widget.setStyleSheet("color: #6b7280; font-size: 11px; font-weight: bold;")
        value_widget = QLabel(value)
        value_widget.setStyleSheet("color: #4f46e5; font-size: 22px; font-weight: bold;")
        card_layout.addWidget(label_widget)
        card_layout.addWidget(value_widget)
        return card

    def create_section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; color: #111827; margin-top: 6px;")
        return label

    def create_list_item(self, title: str, badge: str, description: str | None = None) -> QFrame:
        frame = QFrame()
        frame.setObjectName("ListItem")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #111827;")
        badge_label = QLabel(badge)
        badge_label.setStyleSheet(
            "background: #667eea; color: white; padding: 2px 8px; border-radius: 10px;"
        )
        header.addWidget(title_label)
        header.addStretch(1)
        header.addWidget(badge_label)
        layout.addLayout(header)
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #6b7280; font-size: 12px;")
            layout.addWidget(desc_label)
        return frame


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SeoMcpAgent()
    window.show()
    sys.exit(app.exec())
    