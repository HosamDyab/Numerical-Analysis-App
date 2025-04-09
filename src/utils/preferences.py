import json
import os
import logging
from typing import Dict, Any, Optional

class PreferencesManager:
    """Manages user preferences with validation and error handling."""
    
    # Default preferences
    DEFAULT_PREFERENCES = {
        "theme": "light",
        "decimal_places": 6,
        "max_iterations": 50,
        "epsilon": 0.0001,
        "stop_by_epsilon": True,
        "auto_save": True,
        "recent_files": [],
        "window_size": {
            "width": 1000,
            "height": 700
        }
    }
    
    # Valid themes
    VALID_THEMES = ["light", "dark", "system"]
    
    def __init__(self, file_path: str = "user_preferences.json"):
        """Initialize the preferences manager."""
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
        self.preferences = self.load_preferences()
        
    def load_preferences(self) -> Dict[str, Any]:
        """Load preferences from file or create with defaults."""
        try:
            if not os.path.exists(self.file_path):
                self.logger.info(f"Preferences file not found at {self.file_path}, creating with defaults")
                self.save_preferences(self.DEFAULT_PREFERENCES)
                return self.DEFAULT_PREFERENCES.copy()
                
            with open(self.file_path, 'r', encoding='utf-8') as f:
                loaded_prefs = json.load(f)
                
            # Validate loaded preferences
            validated_prefs = self._validate_preferences(loaded_prefs)
            
            # Update with any missing defaults
            for key, value in self.DEFAULT_PREFERENCES.items():
                if key not in validated_prefs:
                    validated_prefs[key] = value
                    
            return validated_prefs
            
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading preferences: {str(e)}")
            return self.DEFAULT_PREFERENCES.copy()
            
    def _validate_preferences(self, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize preferences."""
        validated = {}
        
        # Validate theme
        theme = prefs.get("theme", self.DEFAULT_PREFERENCES["theme"])
        validated["theme"] = theme if theme in self.VALID_THEMES else self.DEFAULT_PREFERENCES["theme"]
        
        # Validate decimal places
        try:
            decimal_places = int(prefs.get("decimal_places", self.DEFAULT_PREFERENCES["decimal_places"]))
            validated["decimal_places"] = max(1, min(20, decimal_places))  # Limit between 1 and 20
        except (ValueError, TypeError):
            validated["decimal_places"] = self.DEFAULT_PREFERENCES["decimal_places"]
            
        # Validate max iterations
        try:
            max_iter = int(prefs.get("max_iterations", self.DEFAULT_PREFERENCES["max_iterations"]))
            validated["max_iterations"] = max(10, min(1000, max_iter))  # Limit between 10 and 1000
        except (ValueError, TypeError):
            validated["max_iterations"] = self.DEFAULT_PREFERENCES["max_iterations"]
            
        # Validate epsilon
        try:
            epsilon = float(prefs.get("epsilon", self.DEFAULT_PREFERENCES["epsilon"]))
            validated["epsilon"] = max(1e-10, min(1.0, epsilon))  # Limit between 1e-10 and 1.0
        except (ValueError, TypeError):
            validated["epsilon"] = self.DEFAULT_PREFERENCES["epsilon"]
            
        # Validate boolean values
        validated["stop_by_epsilon"] = bool(prefs.get("stop_by_epsilon", self.DEFAULT_PREFERENCES["stop_by_epsilon"]))
        validated["auto_save"] = bool(prefs.get("auto_save", self.DEFAULT_PREFERENCES["auto_save"]))
        
        # Validate recent files
        recent_files = prefs.get("recent_files", [])
        if isinstance(recent_files, list):
            validated["recent_files"] = recent_files[:10]  # Keep only the 10 most recent
        else:
            validated["recent_files"] = []
            
        # Validate window size
        window_size = prefs.get("window_size", self.DEFAULT_PREFERENCES["window_size"])
        if isinstance(window_size, dict):
            try:
                width = int(window_size.get("width", self.DEFAULT_PREFERENCES["window_size"]["width"]))
                height = int(window_size.get("height", self.DEFAULT_PREFERENCES["window_size"]["height"]))
                validated["window_size"] = {
                    "width": max(800, min(1920, width)),  # Limit between 800 and 1920
                    "height": max(600, min(1080, height))  # Limit between 600 and 1080
                }
            except (ValueError, TypeError):
                validated["window_size"] = self.DEFAULT_PREFERENCES["window_size"]
        else:
            validated["window_size"] = self.DEFAULT_PREFERENCES["window_size"]
            
        return validated
        
    def save_preferences(self, preferences: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save preferences to file.
        
        Args:
            preferences: Optional dictionary of preferences to save. If None, saves current preferences.
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            if preferences is not None:
                self.preferences = self._validate_preferences(preferences)
                
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Preferences saved successfully to {self.file_path}")
            return True
            
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Error saving preferences: {str(e)}")
            return False
            
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a preference value.
        
        Args:
            key: The preference key
            default: Default value if key doesn't exist
            
        Returns:
            The preference value or default
        """
        return self.preferences.get(key, default)
        
    def set_preference(self, key: str, value: Any) -> bool:
        """
        Set a preference value.
        
        Args:
            key: The preference key
            value: The value to set
            
        Returns:
            bool: True if set was successful, False otherwise
        """
        try:
            # Create a temporary preferences dict with the new value
            temp_prefs = self.preferences.copy()
            temp_prefs[key] = value
            
            # Validate the new preferences
            validated_prefs = self._validate_preferences(temp_prefs)
            
            # Save if validation passed
            return self.save_preferences(validated_prefs)
            
        except Exception as e:
            self.logger.error(f"Error setting preference {key}: {str(e)}")
            return False
            
    def reset_to_defaults(self) -> bool:
        """
        Reset all preferences to defaults.
        
        Returns:
            bool: True if reset was successful, False otherwise
        """
        return self.save_preferences(self.DEFAULT_PREFERENCES) 