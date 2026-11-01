from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QMessageBox, QFileDialog, QLineEdit, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt
from app.ui.theme import Theme
from app.ui.components.card import Card
from app.ui.components.button import PrimaryButton, SecondaryButton
from app.config.config_manager import ConfigManager
from app.services.data_service import DataService

class SettingsPage(QWidget):
    """Page for configuring application settings and data management."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.config_manager = self.config
        self.data_service = DataService()
        
        from PySide6.QtWidgets import QScrollArea
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(scroll_content)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)
        
        lbl_title = QLabel("Settings")
        lbl_title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 32px; font-weight: bold;")
        self.layout.addWidget(lbl_title)
        
        prefs_card = self.setup_preferences_card()
        self.layout.addWidget(prefs_card)
        
        data_card = self.setup_data_card()
        self.layout.addWidget(data_card)
        
        # AI Config Card
        ai_card = QWidget()
        ai_card.setObjectName("SettingsCard")
        self.setup_ai_card(ai_card)
        self.layout.addWidget(ai_card)
        
        self.layout.addStretch()
        
    def setup_preferences_card(self):
        card = Card()
        layout = QVBoxLayout()
        
        lbl_header = QLabel("Preferences")
        lbl_header.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        layout.addWidget(lbl_header)
        
        self.chk_sound = QCheckBox("Enable Alarm Sound")
        self.chk_sound.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        self.chk_sound.setChecked(self.config.get("sound_enabled", True))
        self.chk_sound.toggled.connect(lambda c: self.config.set("sound_enabled", c))
        self.chk_sound.toggled.connect(lambda: self.save_settings())
        layout.addWidget(self.chk_sound)
        self.cb_sound = self.chk_sound
        
        self.chk_notif = QCheckBox("Enable Desktop Notifications")
        self.chk_notif.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        self.chk_notif.setChecked(self.config.get("notifications_enabled", True))
        self.chk_notif.toggled.connect(lambda c: self.config.set("notifications_enabled", c))
        self.chk_notif.toggled.connect(lambda: self.save_settings())
        layout.addWidget(self.chk_notif)
        self.cb_notifications = self.chk_notif
        
        card.addLayout(layout)
        return card
        
    def setup_data_card(self):
        card = Card()
        layout = QVBoxLayout()
        
        lbl_header = QLabel("Data Management")
        lbl_header.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        layout.addWidget(lbl_header)
        
        lbl_desc = QLabel("Export your sessions for backup or analysis.")
        lbl_desc.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        layout.addWidget(lbl_desc)
        
        btn_layout = QHBoxLayout()
        
        btn_csv = SecondaryButton("Export CSV")
        btn_csv.clicked.connect(self.export_csv)
        btn_layout.addWidget(btn_csv)
        
        btn_json = SecondaryButton("Export JSON")
        btn_json.clicked.connect(self.export_json)
        btn_layout.addWidget(btn_json)
        
        btn_ml = SecondaryButton("Export ML Dataset")
        btn_ml.setStyleSheet(f"background-color: {Theme.PRIMARY_ACCENT}; color: {Theme.TEXT_PRIMARY};")
        btn_ml.clicked.connect(self.export_ml_dataset)
        btn_layout.addWidget(btn_ml)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        card.addLayout(layout)
        return card

    def setup_ai_card(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("AI Study Coach & LLM Providers")
        title.setObjectName("CardTitle")
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        desc = QLabel("Use Google Gemini and optionally a compatible hosted API as a fallback when a provider is unavailable or reaches its quota.")
        desc.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 13px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Provider Priority
        priority_layout = QHBoxLayout()
        priority_label = QLabel("Provider Priority:")
        priority_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        self.priority_combo = QComboBox()
        self.priority_combo.addItem("Google Gemini → Compatible API fallback", "gemini_first")
        self.priority_combo.addItem("Compatible API → Gemini fallback", "compatible_api_first")
        self.priority_combo.addItem("Google Gemini only", "gemini_only")
        self.priority_combo.addItem("Compatible API only", "compatible_api_only")
        self.priority_combo.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 6px; border-radius: 4px;")

        curr_prio = self.config_manager.get("llm_provider_priority", "gemini_first")
        idx = self.priority_combo.findData(curr_prio)
        if idx >= 0:
            self.priority_combo.setCurrentIndex(idx)
        self.priority_combo.currentIndexChanged.connect(self.save_settings)
        priority_layout.addWidget(priority_label)
        priority_layout.addWidget(self.priority_combo)
        layout.addLayout(priority_layout)

        # Gemini Cloud Section Header
        lbl_gemini = QLabel("Cloud LLM (Google Gemini)")
        lbl_gemini.setStyleSheet(f"color: {Theme.PRIMARY_ACCENT}; font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(lbl_gemini)

        key_layout = QHBoxLayout()
        key_label = QLabel("Google Gemini API Key:")
        key_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your Google Gemini API Key...")
        self.api_key_input.setText(self.config_manager.get("gemini_api_key", ""))
        self.api_key_input.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 6px;")
        self.api_key_input.textChanged.connect(self.save_settings)
        
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.api_key_input)
        layout.addLayout(key_layout)
        
        # Cloud Privacy Consent
        self.chk_cloud_consent = QCheckBox("Allow sending study context to Gemini and compatible API providers")
        self.chk_cloud_consent.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        self.chk_cloud_consent.setChecked(self.config_manager.get("cloud_consent", False))
        self.chk_cloud_consent.toggled.connect(self.save_settings)
        layout.addWidget(self.chk_cloud_consent)

        lbl_compatible = QLabel("Other OpenAI-compatible hosted APIs")
        lbl_compatible.setStyleSheet(f"color: {Theme.PRIMARY_ACCENT}; font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(lbl_compatible)
        compatible_note = QLabel(
            "Configure any service that implements POST /chat/completions. Check the provider's current free-tier, rate limits, and terms; availability and free quotas vary."
        )
        compatible_note.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px;")
        compatible_note.setWordWrap(True)
        layout.addWidget(compatible_note)
        self.compatible_api_label_input = QLineEdit(self.config_manager.get("compatible_api_label", "Compatible API"))
        self.compatible_api_label_input.setPlaceholderText("Provider display name")
        self.compatible_api_base_url_input = QLineEdit(self.config_manager.get("compatible_api_base_url", ""))
        self.compatible_api_base_url_input.setPlaceholderText("HTTPS base URL, e.g. https://api.provider.example/v1")
        self.compatible_api_model_input = QLineEdit(self.config_manager.get("compatible_api_model", ""))
        self.compatible_api_model_input.setPlaceholderText("Model ID")
        self.compatible_api_key_input = QLineEdit(self.config_manager.get("compatible_api_key", ""))
        self.compatible_api_key_input.setEchoMode(QLineEdit.Password)
        self.compatible_api_key_input.setPlaceholderText("Provider API key")
        for field in (
            self.compatible_api_label_input,
            self.compatible_api_base_url_input,
            self.compatible_api_model_input,
            self.compatible_api_key_input,
        ):
            field.setStyleSheet(f"background-color: {Theme.BACKGROUND_DARK}; color: {Theme.TEXT_PRIMARY}; padding: 6px;")
            field.textChanged.connect(self.save_settings)
            layout.addWidget(field)
        
        btn_layout = QHBoxLayout()
        btn_rebuild_rag = SecondaryButton("Rebuild Knowledge Index")
        btn_rebuild_rag.clicked.connect(self.rebuild_rag_index)
        btn_layout.addWidget(btn_rebuild_rag)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
    def rebuild_rag_index(self):
        try:
            from app.services.rag_service import RAGService
            rag = RAGService()
            rag.rebuild_index()
            QMessageBox.information(self, "RAG Rebuild", f"Successfully rebuilt the knowledge index. Now tracking {rag.count()} chunks.")
        except Exception as e:
            QMessageBox.warning(self, "RAG Rebuild Failed", f"Failed to rebuild knowledge index:\n{e}")
        
    def save_settings(self):
        self.config_manager.set("sound_enabled", self.cb_sound.isChecked())
        notif = self.cb_notifications.isChecked()
        self.config_manager.set("notifications_enabled", notif)
        self.config_manager.set("desktop_notifications", notif)
        self.config_manager.set("gemini_api_key", self.api_key_input.text())
        if hasattr(self, 'priority_combo'):
            self.config_manager.set("llm_provider_priority", self.priority_combo.currentData())
        if hasattr(self, 'compatible_api_base_url_input'):
            self.config_manager.set("compatible_api_label", self.compatible_api_label_input.text().strip())
            self.config_manager.set("compatible_api_base_url", self.compatible_api_base_url_input.text().strip())
            self.config_manager.set("compatible_api_key", self.compatible_api_key_input.text().strip())
            self.config_manager.set("compatible_api_model", self.compatible_api_model_input.text().strip())
        if hasattr(self, 'chk_cloud_consent'):
            self.config_manager.set("cloud_consent", self.chk_cloud_consent.isChecked())
            self.config_manager.set("cloud_consent_configured", True)
        
    def export_csv(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if filepath:
            if self.data_service.export_csv(filepath):
                QMessageBox.information(self, "Export Successful", f"Data exported to:\n{filepath}")
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to export data to CSV.")
                
    def export_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export JSON", "", "JSON Files (*.json)")
        if filepath:
            if self.data_service.export_json(filepath):
                QMessageBox.information(self, "Export Successful", f"Data exported to:\n{filepath}")
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to export data to JSON.")
                
    def export_ml_dataset(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export ML Dataset", "ml_dataset.csv", "CSV Files (*.csv)")
        if filepath:
            if self.data_service.export_ml_dataset(filepath):
                QMessageBox.information(self, "Export Successful", f"ML Dataset generated and exported to:\n{filepath}")
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to generate ML dataset (ensure you have completed sessions!).")
                
