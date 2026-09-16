# Theme definitions for StudyTrack

class Theme:
    # Colors
    BACKGROUND_DARK = "#0a0a0f"
    BACKGROUND_CARD = "#14141e"
    BACKGROUND_CARD_HOVER = "#1c1c2a"
    
    PRIMARY_ACCENT = "#7b61ff" # Purple/violet
    PRIMARY_ACCENT_HOVER = "#8f79ff"
    
    SECONDARY_ACCENT = "#2563eb" # Blue
    
    SUCCESS_COLOR = "#10b981" # Green
    WARNING_COLOR = "#f59e0b" # Orange/yellow
    
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#9ca3af"
    
    BORDER_COLOR = "#2a2a3a"
    
    # Fonts
    FONT_FAMILY = "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif"
    FONT_SIZE_SMALL = "12px"
    FONT_SIZE_REGULAR = "14px"
    FONT_SIZE_LARGE = "18px"
    FONT_SIZE_XLARGE = "24px"
    FONT_SIZE_XXLARGE = "36px"
    
    # Spacing
    SPACING_SMALL = 8
    SPACING_REGULAR = 16
    SPACING_LARGE = 24

GLOBAL_STYLESHEET = f"""
QWidget {{
    background-color: {Theme.BACKGROUND_DARK};
    color: {Theme.TEXT_PRIMARY};
    font-family: {Theme.FONT_FAMILY};
    font-size: {Theme.FONT_SIZE_REGULAR};
}}

/* Scrollbar styles for a clean dark look */
QScrollBar:vertical {{
    background-color: {Theme.BACKGROUND_DARK};
    width: 12px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background-color: {Theme.BORDER_COLOR};
    min-height: 20px;
    border-radius: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {Theme.TEXT_SECONDARY};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""
