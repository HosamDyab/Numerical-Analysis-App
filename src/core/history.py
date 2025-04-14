import json
import os
import shutil
from typing import List, Dict, Any, Optional, Union
import logging
from datetime import datetime

class HistoryManager:
    def __init__(self, file_path: str = "history.json"):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
        self.backup_dir = "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Create history file if it doesn't exist
        if not os.path.exists(self.file_path):
            self._save_empty_history()

    def _save_empty_history(self) -> None:
        """Create an empty history file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            self.logger.info(f"Created empty history file at {self.file_path}")
        except IOError as e:
            self.logger.error(f"Failed to create empty history file: {str(e)}")
            raise

    def _create_backup(self) -> Optional[str]:
        """Create a backup of the history file."""
        try:
            if not os.path.exists(self.file_path):
                return None
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"history_{timestamp}.json")
            
            shutil.copy2(self.file_path, backup_path)
            self.logger.info(f"Created backup at {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create backup: {str(e)}")
            return None

    def _validate_solution_data(self, func: str, method: str, root: Union[float, List[float]], table: List[Dict[str, Any]]) -> bool:
        """Validate the solution data before saving."""
        if not isinstance(func, str) or not func:
            self.logger.error("Invalid function: must be a non-empty string")
            return False
            
        if not isinstance(method, str) or not method:
            self.logger.error("Invalid method: must be a non-empty string")
            return False
            
        # Check if the method is a linear system method
        if method in ["Gauss Elimination", "Gauss Elimination (Partial Pivoting)", 
                     "LU Decomposition", "LU Decomposition (Partial Pivoting)",
                     "Gauss-Jordan", "Gauss-Jordan (Partial Pivoting)"]:
            # For linear system methods, root should be a list of floats
            if not isinstance(root, list):
                self.logger.error(f"Invalid root value for linear system method: {root}")
                return False
            
            if not all(isinstance(val, (int, float)) for val in root):
                self.logger.error(f"Invalid root values in list: {root}")
                return False
        else:
            # For other methods, root should be a single float
            if not isinstance(root, (int, float)):
                self.logger.error(f"Invalid root value: {root}")
                return False
            
        if not isinstance(table, list):
            self.logger.error("Invalid table: must be a list")
            return False
            
        if table and not all(isinstance(row, dict) for row in table):
            self.logger.error("Invalid table: all rows must be dictionaries")
            return False
            
        return True

    def save_solution(self, func: str, method: str, root: Union[float, List[float]], table: List[Dict[str, Any]]) -> bool:
        """
        Save a solution to the history with validation and backup.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Validate data
            if not self._validate_solution_data(func, method, root, table):
                return False
                
            # Create backup before modifying
            self._create_backup()
            
            # Load and update history
            history = self.load_history()
            history.append({
                "function": func,
                "method": method,
                "root": root,
                "table": table,
                "timestamp": datetime.now().isoformat()
            })
            
            # Save updated history
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Successfully saved solution for {method} method")
            return True
            
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Error saving history: {str(e)}")
            return False

    def load_history(self) -> List[Dict[str, Any]]:
        """Load the history with error handling."""
        try:
            if not os.path.exists(self.file_path):
                self.logger.warning(f"History file not found at {self.file_path}, creating empty history")
                self._save_empty_history()
                return []
                
            with open(self.file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
                
            if not isinstance(history, list):
                self.logger.error("History file corrupted: not a list")
                return []
                
            return history
            
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading history: {str(e)}")
            return []

    def clear_history(self) -> bool:
        """
        Clear the history with backup.
        
        Returns:
            bool: True if clear was successful, False otherwise
        """
        try:
            if os.path.exists(self.file_path):
                # Create backup before clearing
                self._create_backup()
                
                # Clear the file
                self._save_empty_history()
                self.logger.info("History cleared successfully")
                return True
            return True  # Nothing to clear
            
        except IOError as e:
            self.logger.error(f"Error clearing history: {str(e)}")
            return False
            
    def get_recent_solutions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent solutions.
        
        Args:
            limit: Maximum number of solutions to return
            
        Returns:
            List of recent solutions
        """
        history = self.load_history()
        return history[-limit:] if history else []