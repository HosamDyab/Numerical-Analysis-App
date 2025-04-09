import customtkinter as ctk
from typing import Dict, Optional
import logging

class ThemeManager:
    LIGHT_MODE: Dict[str, str] = {
        "bg": "#F0F4F8",       # Soft light gray
        "fg": "#DDE4E6",       # Lighter gray for sidebar
        "text": "#2D3748",     # Dark gray for readability
        "button": "#4C51BF",   # Darker blue (changed from light purple-blue)
        "button_hover": "#2D3748",  # Even darker blue on hover
        "accent": "#4C51BF",   # Deep blue for highlights
        "table_bg": "#FFFFFF", # White for table background
        "table_fg": "#2D3748", # Dark gray for table text
        "table_heading_bg": "#E2E8F0", # Light gray for table headers
        "table_heading_fg": "#2D3748",  # Dark gray for header text
        "table_odd_row": "#F8FAFC", # Very light gray for odd rows
        "table_even_row": "#FFFFFF", # White for even rows
        "table_hover": "#E2E8F0" # Light gray for hover
    }
    DARK_MODE: Dict[str, str] = {
        "bg": "#121212",       # True dark background (Material Design dark theme)
        "fg": "#1E1E1E",       # Slightly lighter dark for sidebar
        "text": "#E0E0E0",     # Light gray for better readability
        "button": "#3A86FF",   # Vibrant blue for buttons
        "button_hover": "#5A9AFF",  # Lighter blue on hover
        "accent": "#00B4D8",   # Cyan accent for highlights
        "table_bg": "#0A0A0A", # Darker background for table
        "table_fg": "#FFFFFF", # White for table text for better visibility
        "table_heading_bg": "#1A1A1A", # Darker for table headers
        "table_heading_fg": "#FFFFFF",  # White for header text
        "table_odd_row": "#0D0D0D", # Slightly lighter for odd rows
        "table_even_row": "#0A0A0A", # Darker for even rows
        "table_hover": "#1E1E1E" # Hover color for rows
    }
    BLUE_MODE: Dict[str, str] = {
        "bg": "#2B6CB0",       # Medium blue
        "fg": "#2C5282",       # Darker blue for sidebar
        "text": "#EBF8FF",     # Very light blue for text
        "button": "#4299E1",   # Bright blue
        "button_hover": "#2B6CB0",  # Slightly darker blue
        "accent": "#FFFFFF",   # White for highlights
        "table_bg": "#EBF8FF", # Very light blue for table background
        "table_fg": "#2C5282", # Dark blue for table text
        "table_heading_bg": "#4299E1", # Bright blue for table headers
        "table_heading_fg": "#FFFFFF",  # White for header text
        "table_odd_row": "#EBF8FF", # Very light blue for odd rows
        "table_even_row": "#E6FFFA", # Slightly different light blue for even rows
        "table_hover": "#BEE3F8" # Light blue for hover
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.themes = {
            "Light": self.LIGHT_MODE,
            "Dark": self.DARK_MODE,
            "Blue": self.BLUE_MODE
        }
        self.current_theme = "Light"
        try:
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
        except Exception as e:
            self.logger.error(f"Error initializing theme: {str(e)}")
            raise

    def apply_theme(self) -> Dict[str, str]:
        """Apply the current theme and return the theme dictionary."""
        try:
            return self.themes[self.current_theme]
        except KeyError:
            self.logger.error(f"Invalid theme: {self.current_theme}")
            return self.LIGHT_MODE  # Fallback to light mode

    def set_theme(self, theme_name: str) -> Dict[str, str]:
        """
        Set the current theme and update the appearance mode.
        
        Args:
            theme_name: Name of the theme to set
            
        Returns:
            The theme dictionary for the selected theme
            
        Raises:
            KeyError: If the theme name is invalid
        """
        try:
            if theme_name not in self.themes:
                raise KeyError(f"Invalid theme name: {theme_name}")
            
            self.current_theme = theme_name
            # Update the appearance mode for all widgets
            ctk.set_appearance_mode("light" if theme_name == "Light" else "dark")
            # Force update the default color theme
            ctk.set_default_color_theme("blue")
            # Return the new theme dictionary
            return self.themes[theme_name]
        except Exception as e:
            self.logger.error(f"Error setting theme: {str(e)}")
            raise