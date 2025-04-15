import json
import os
from typing import List, Dict, Any, Optional, Union

class HistoryManager:
    def __init__(self, file_path: str = "history.json"):
        self.file_path = file_path
        
        # Create history file if it doesn't exist
        if not os.path.exists(self.file_path):
            self._save_empty_history()

    def _save_empty_history(self) -> None:
        """Create an empty history file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Failed to create empty history file: {str(e)}")
            raise

    def _validate_solution_data(self, func: str, method: str, root: Union[float, List[float]], table: List[Dict[str, Any]]) -> bool:
        """Validate the solution data before saving."""
        if not isinstance(func, str) or not func:
            return False
            
        if not isinstance(method, str) or not method:
            return False
            
        if not isinstance(table, list):
            return False
            
        return True

    def save_solution(self, func: str, method: str, root: Union[float, List[float]], table: List[Dict[str, Any]], params: Dict[str, Any] = None) -> bool:
        """Save a solution to the history file."""
        if not self._validate_solution_data(func, method, root, table):
            return False
            
        try:
            # Load existing history
            history = self.load_history()
            
            # Create solution entry
            solution = {
                "function": func,
                "method": method,
                "root": root,
                "iterations": table,
                "parameters": params or {}
            }
            
            # Add to history
            history.append(solution)
            
            # Save updated history
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"Failed to save solution: {str(e)}")
            return False

    def load_history(self) -> List[Dict[str, Any]]:
        """Load the solution history."""
        try:
            if not os.path.exists(self.file_path):
                return []
                
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load history: {str(e)}")
            return []

    def clear_history(self) -> bool:
        """Clear the solution history."""
        try:
            self._save_empty_history()
            return True
        except Exception as e:
            print(f"Failed to clear history: {str(e)}")
            return False

    def get_solution(self, index: int) -> Optional[Dict[str, Any]]:
        """Get a specific solution by index."""
        history = self.load_history()
        
        if 0 <= index < len(history):
            return history[index]
        else:
            return None

    def delete_solution(self, index: int) -> bool:
        """Delete a specific solution by index."""
        try:
            history = self.load_history()
            
            if 0 <= index < len(history):
                del history[index]
                
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
                    
                return True
            else:
                return False
        except Exception as e:
            print(f"Failed to delete solution: {str(e)}")
            return False