from tkinter import ttk
from typing import List, Dict, Any
import logging

class ResultTable:
    def __init__(self, parent):
        self.parent = parent
        self.table_frame = ttk.Frame(parent)
        self.table_frame.pack(side="top", fill="both", expand=True)
        
        # Create a scrollbar
        self.scrollbar = ttk.Scrollbar(self.table_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        # Create the table with scrollbar
        self.table = ttk.Treeview(
            self.table_frame,
            show="headings",
            style="Custom.Treeview",
            height=10,
            yscrollcommand=self.scrollbar.set
        )
        self.table.pack(side="left", fill="both", expand=True)
        
        # Configure scrollbar
        self.scrollbar.config(command=self.table.yview)
        
        self.logger = logging.getLogger(__name__)

    def clear_table(self) -> None:
        """Clear all items from the table."""
        try:
            for item in self.table.get_children():
                self.table.delete(item)
        except Exception as e:
            self.logger.error(f"Error clearing table: {str(e)}")

    def setup_columns(self, columns: List[str]) -> None:
        """Set up table columns with proper configuration."""
        try:
            # Clear existing columns
            for col in self.table["columns"]:
                self.table.heading(col, text="")
                self.table.column(col, width=0)
            
            # Set new columns
            self.table["columns"] = columns
            for col in columns:
                self.table.heading(col, text=col)
                self.table.column(col, width=120, anchor="center", stretch=True)
        except Exception as e:
            self.logger.error(f"Error setting up columns: {str(e)}")

    def display(self, table_data: List[Dict[str, Any]]) -> None:
        """Display the solution data in the table."""
        try:
            self.clear_table()
            
            if not table_data:
                self.setup_columns(["Message"])
                self.table.insert("", "end", values=["No data available"])
                return

            # Handle error case
            if isinstance(table_data, dict) and "Error" in table_data:
                self.setup_columns(["Message"])
                self.table.insert("", "end", values=[table_data.get("Error", "Unknown error")])
                return

            # Ensure table_data is a list
            if not isinstance(table_data, list):
                table_data = [table_data]

            # Get columns from first row
            if not table_data:
                self.setup_columns(["Message"])
                self.table.insert("", "end", values=["No data available"])
                return

            first_row = table_data[0]
            if not isinstance(first_row, dict):
                self.setup_columns(["Message"])
                self.table.insert("", "end", values=["Invalid data format"])
                return

            columns = list(first_row.keys())
            self.setup_columns(columns)
            
            # Insert data
            for row in table_data:
                if not isinstance(row, dict):
                    continue
                values = [str(row.get(col, "")) for col in columns]
                self.table.insert("", "end", values=values)
                
            # Configure column widths based on content
            for col in columns:
                max_width = max(
                    len(str(col)) * 10,  # Header width
                    max(len(str(row.get(col, ""))) * 10 for row in table_data)  # Content width
                )
                self.table.column(col, width=min(max_width, 200))
        except Exception as e:
            self.logger.error(f"Error displaying table data: {str(e)}")
            self.clear_table()
            self.setup_columns(["Error"])
            self.table.insert("", "end", values=[f"Error displaying data: {str(e)}"])

    def display_history(self, history: List[Dict[str, Any]]) -> None:
        """Display the history data in the table."""
        try:
            self.clear_table()
            self.setup_columns(["Function", "Method", "Root"])
            
            if not history:
                self.table.insert("", "end", values=["No history available"])
                return

            for entry in history:
                if not isinstance(entry, dict):
                    continue
                self.table.insert("", "end", values=(
                    str(entry.get("function", "")),
                    str(entry.get("method", "")),
                    str(entry.get("root", ""))
                ))
                
            # Configure column widths
            for col in ["Function", "Method", "Root"]:
                max_width = max(
                    len(str(col)) * 10,
                    max(len(str(entry.get(col, ""))) * 10 for entry in history)
                )
                self.table.column(col, width=min(max_width, 200))
        except Exception as e:
            self.logger.error(f"Error displaying history: {str(e)}")
            self.clear_table()
            self.setup_columns(["Error"])
            self.table.insert("", "end", values=[f"Error displaying history: {str(e)}"])