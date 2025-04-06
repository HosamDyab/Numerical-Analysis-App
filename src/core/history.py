import json
import os
from typing import List, Dict, Any
import logging

class HistoryManager:
    def __init__(self, file_path: str = "history.json"):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)

    def save_solution(self, func: str, method: str, root: float, table: List[Dict[str, Any]]) -> None:
        try:
            history = self.load_history()
            history.append({
                "function": func,
                "method": method,
                "root": root,
                "table": table
            })
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Error saving history: {str(e)}")
            raise

    def load_history(self) -> List[Dict[str, Any]]:
        try:
            if not os.path.exists(self.file_path):
                return []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading history: {str(e)}")
            return []

    def clear_history(self) -> None:
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
        except IOError as e:
            self.logger.error(f"Error clearing history: {str(e)}")
            raise