from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QMessageBox, QFileDialog, QLineEdit, QGroupBox
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
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE, Theme.SPACING_LARGE)
        self.layout.setSpacing(Theme.SPACING_LARGE)
        
        lbl_title = QLabel("Settings")
        lbl_title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 32px; font-weight: bold;")
        self.layout.addWidget(lbl_title)
        
        self.setup_preferences_card()
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
        
        layout.addSpacing(20)
        
        btn_wipe = PrimaryButton("Wipe All Data")
        btn_wipe.setStyleSheet(f"background-color: {Theme.DANGER_COLOR};")
        btn_wipe.clicked.connect(self.wipe_data)
        layout.addWidget(btn_wipe)
        
        card.addLayout(layout)
        return card

    def setup_ai_card(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("AI Study Coach Configuration")
        title.setObjectName("CardTitle")
        layout.addWidget(title)
        
        key_layout = QHBoxLayout()
        key_label = QLabel("Google Gemini API Key:")
        key_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter your API Key here...")
        self.api_key_input.setText(self.config_manager.get("gemini_api_key", ""))
        self.api_key_input.textChanged.connect(self.save_settings)
        
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.api_key_input)
        layout.addLayout(key_layout)
        
        info = QLabel("The API key is required to use the real AI Coach. If left blank, a Mock AI will be used.")
        info.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 12px; font-style: italic;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
    def save_settings(self):
        self.config_manager.set("sound_enabled", self.cb_sound.isChecked())
        notif = self.cb_notifications.isChecked()
        self.config_manager.set("notifications_enabled", notif)
        self.config_manager.set("desktop_notifications", notif)
        self.config_manager.set("gemini_api_key", self.api_key_input.text())
        
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
                
    def wipe_data(self):
        reply = QMessageBox.question(
            self, 
            "Confirm Data Wipe",
            "Are you absolutely sure you want to delete all study sessions? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.data_service.wipe_all_data():
                QMessageBox.information(self, "Data Wiped", "All study sessions have been deleted.")
            else:
                QMessageBox.warning(self, "Error", "An error occurred while wiping data.")
