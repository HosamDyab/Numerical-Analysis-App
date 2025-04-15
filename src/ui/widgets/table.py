import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import List, Dict, Any
import logging
import numpy as np

class ResultTable:
    def __init__(self, parent, theme=None):
        self.theme = theme or {}
        self.table_frame = ctk.CTkFrame(parent, fg_color=self.theme.get("bg", "#F0F4F8"))
        self.table_frame.pack(fill="both", expand=True)
        
        # Create a canvas with scrollbar
        self.canvas = tk.Canvas(self.table_frame, bg=self.theme.get("bg", "#F0F4F8"), highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color=self.theme.get("bg", "#F0F4F8"))
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_width())
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Create the table
        self.table = ttk.Treeview(self.scrollable_frame, style="Custom.Treeview", show="headings")
        self.table.pack(fill="both", expand=True)
        
        # Configure hover effect
        hover_color = self.theme.get("table_hover", "#E2E8F0")
        self.table.tag_configure('hover', background=hover_color)
        
        # Configure alternating row colors
        odd_row_color = self.theme.get("table_odd_row", "#F8FAFC")
        even_row_color = self.theme.get("table_even_row", "#FFFFFF")
        self.table.tag_configure('oddrow', background=odd_row_color)
        self.table.tag_configure('evenrow', background=even_row_color)
        
        # Bind hover events
        self.table.bind('<Enter>', lambda e: self.on_enter(e))
        self.table.bind('<Leave>', lambda e: self.on_leave(e))
        
        # Configure mouse wheel scrolling - use a more robust approach
        self.table.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Bind resize event to update canvas width
        self.table_frame.bind("<Configure>", self._on_frame_resize)
        
        self.logger = logging.getLogger(__name__)
        
    def _on_frame_resize(self, event):
        """Update the canvas width when the frame is resized."""
        try:
            # Check if widgets still exist
            if not self.table_frame.winfo_exists() or not self.canvas.winfo_exists():
                return
                
            # Get the canvas window item
            canvas_items = self.canvas.find_withtag("all")
            if not canvas_items:
                return
                
            # Calculate new width (accounting for scrollbar)
            new_width = event.width - self.scrollbar.winfo_width()
            if new_width <= 0:
                new_width = 100  # Minimum width
                
            # Update the canvas window width
            self.canvas.itemconfig(canvas_items[0], width=new_width)
            
            # Update column widths if table exists and has columns
            if hasattr(self, "table") and self.table.winfo_exists() and self.table["columns"]:
                columns = self.table["columns"]
                column_width = max(150, new_width // len(columns))
                
                for col in columns:
                    self.table.column(col, width=column_width)
                    
        except Exception as e:
            self.logger.error(f"Error in frame resize handler: {str(e)}")
            # Continue execution even if there's an error
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling with error handling."""
        try:
            # Check if the widget still exists
            if not self.canvas.winfo_exists():
                return
                
            # Calculate scroll amount based on event delta
            # Different platforms may have different delta values
            if hasattr(event, 'delta'):
                # Windows
                scroll_amount = int(-1 * (event.delta / 120))
            elif hasattr(event, 'num'):
                # Linux
                scroll_amount = -1 if event.num == 4 else 1
            else:
                # Default fallback
                scroll_amount = -1
                
            # Perform the scroll
            self.canvas.yview_scroll(scroll_amount, "units")
        except Exception as e:
            self.logger.error(f"Error in mousewheel handler: {str(e)}")
            # Continue execution even if there's an error
        
    def on_enter(self, event):
        """Handle mouse enter event with error handling."""
        try:
            # Check if widgets still exist
            if not self.table.winfo_exists():
                return
                
            item = self.table.identify_row(event.y)
            if item:
                self.table.item(item, tags=('hover',))
        except Exception as e:
            self.logger.error(f"Error in on_enter handler: {str(e)}")
            
    def on_leave(self, event):
        """Handle mouse leave event with error handling."""
        try:
            # Check if widgets still exist
            if not self.table.winfo_exists():
                return
                
            item = self.table.identify_row(event.y)
            if item:
                # Restore original row color
                row_idx = self.table.index(item)
                tag = 'evenrow' if row_idx % 2 == 0 else 'oddrow'
                self.table.item(item, tags=(tag,))
        except Exception as e:
            self.logger.error(f"Error in on_leave handler: {str(e)}")        
    def update_theme(self, theme):
        """Update the table theme colors."""
        try:
            # Check if widgets still exist
            if not self.table_frame.winfo_exists():
                return
                
            self.theme = theme
            
            # Update frame colors
            self.table_frame.configure(fg_color=self.theme.get("bg", "#F0F4F8"))
            
            if self.canvas.winfo_exists():
                self.canvas.configure(bg=self.theme.get("bg", "#F0F4F8"))
                
            if self.scrollable_frame.winfo_exists():
                self.scrollable_frame.configure(fg_color=self.theme.get("bg", "#F0F4F8"))
            
            # Update hover and row colors
            hover_color = self.theme.get("table_hover", "#E2E8F0")
            odd_row_color = self.theme.get("table_odd_row", "#F8FAFC")
            even_row_color = self.theme.get("table_even_row", "#FFFFFF")
            
            if self.table.winfo_exists():
                self.table.tag_configure('hover', background=hover_color)
                self.table.tag_configure('oddrow', background=odd_row_color)
                self.table.tag_configure('evenrow', background=even_row_color)
                
                # Update table style
                style = ttk.Style()
                style.configure("Custom.Treeview",
                              background=self.theme.get("table_bg", "#F0F4F8"),
                              foreground=self.theme.get("table_fg", "#1E293B"),
                              fieldbackground=self.theme.get("table_bg", "#F0F4F8"))
                
                style.configure("Custom.Treeview.Heading",
                              background=self.theme.get("table_heading_bg", "#E2E8F0"),
                              foreground=self.theme.get("table_heading_fg", "#1E293B"))
                
                # Reapply row colors to existing rows
                for item in self.table.get_children():
                    row_idx = self.table.index(item)
                    tag = 'evenrow' if row_idx % 2 == 0 else 'oddrow'
                    self.table.item(item, tags=(tag,))
            
            # Update scrollbar appearance
            if self.scrollbar.winfo_exists():
                self.scrollbar.configure(style="Custom.Vertical.TScrollbar")
                style = ttk.Style()
                style.configure("Custom.Vertical.TScrollbar", 
                              background=self.theme.get("scrollbar_bg", "#CBD5E1"),
                              troughcolor=self.theme.get("scrollbar_trough", "#F1F5F9"),
                              arrowcolor=self.theme.get("scrollbar_arrow", "#64748B"))
            
        except Exception as e:
            self.logger.error(f"Error updating table theme: {str(e)}")
            # Continue execution even if there's an error
        
    def _format_matrix(self, matrix: np.ndarray, decimal_places: int) -> str:
        """Format the matrix for display."""
        n = matrix.shape[0]
        formatted = []
        for i in range(n):
            row = []
            for j in range(n):
                value = self._format_value(matrix[i, j], decimal_places)
                # Add fixed-width spacing (20 characters) for each number
                row.append(f"{value:>20}")
            formatted.append("    ".join(row))  # Add 4 spaces between numbers
        return "\n\n".join(formatted)  # Add extra line between rows

    def _format_vector(self, vector: np.ndarray, decimal_places: int) -> str:
        """Format the vector for display."""
        formatted = []
        for value in vector:
            # Add fixed-width spacing (20 characters) for each number
            formatted.append(f"{self._format_value(value, decimal_places):>20}")
        return "\n\n".join(formatted)  # Add extra line between rows

    def display(self, data: List[Dict]):
        """Display the data in the table."""
        try:
            # Clear existing items
            for item in self.table.get_children():
                self.table.delete(item)
            
            # Check if we have an error message
            if len(data) == 1 and "Error" in data[0]:
                self.table["columns"] = ["Error"]
                self.table.column("Error", anchor="center", width=800)
                self.table.heading("Error", text="Error", anchor="center")
                self.table.insert("", "end", values=(data[0]["Error"],), tags=('oddrow',))
                return
            
            # Configure columns based on the first row
            if data:
                # Get the actual column names from the data
                columns = list(data[0].keys())
                
                # Set the columns
                self.table["columns"] = columns
                
                # Calculate column width based on available space
                available_width = self.table_frame.winfo_width() - self.scrollbar.winfo_width()
                if available_width <= 0:
                    available_width = 1800  # Increased default width for better display
                    
                # Special handling for Gauss Elimination
                if "Matrix" in columns or "Vector" in columns:
                    # Make Matrix and Vector columns wider
                    column_widths = {}
                    for col in columns:
                        if col == "Matrix":
                            column_widths[col] = 1200  # Much wider for augmented matrix display
                        elif col == "Step":
                            column_widths[col] = 200  # Fixed width for step column
                        elif col == "Operation":
                            column_widths[col] = 600  # Wider for operation description and error
                        else:
                            column_widths[col] = max(100, available_width // len(columns))
                else:
                    # Default column widths for other methods
                    column_widths = {col: max(100, available_width // len(columns)) for col in columns}
                
                # Configure columns with calculated widths
                for col in columns:
                    self.table.column(col, anchor="center", width=column_widths[col])
                    self.table.heading(col, text=col, anchor="center")
                
                # Set row height
                style = ttk.Style()
                # Check if this is a root-finding method by looking at the column names
                if any(col in columns for col in ["Xl", "Xu", "Xr", "Xi", "Xi-1", "f(Xi)", "g(Xi)"]):
                    # Root-finding methods need less row height
                    style.configure("Custom.Treeview", rowheight=25)  # Smaller row height for root-finding methods
                else:
                    # Matrix methods need more space
                    style.configure("Custom.Treeview", rowheight=200)  # Larger row height for matrix methods
            
            # Add new items
            for i, row in enumerate(data):
                values = []
                
                # Extract values in the correct order
                for col in self.table["columns"]:
                    value = row.get(col, "")
                    
                    # Format numeric values
                    if isinstance(value, (int, float)):
                        # Check if it's an integer
                        if value.is_integer() if isinstance(value, float) else True:
                            # Format as integer
                            values.append(str(int(value)))
                        else:
                            # Format as decimal with trailing zeros removed
                            str_value = f"{value:.6f}"
                            str_value = str_value.rstrip('0').rstrip('.')
                            values.append(str_value)
                    else:
                        # Handle matrix and vector strings
                        if col in ["Matrix", "Vector", "Solution"]:
                            # Split the string into lines
                            lines = value.split('\n')
                            # Format each line to remove trailing zeros
                            formatted_lines = []
                            for line in lines:
                                numbers = line.split()
                                formatted_numbers = []
                                for num in numbers:
                                    try:
                                        num_float = float(num)
                                        if num_float.is_integer():
                                            formatted_numbers.append(f"{int(num_float):>20}")
                                        else:
                                            formatted_num = f"{num_float:.6f}".rstrip('0').rstrip('.')
                                            formatted_numbers.append(f"{formatted_num:>20}")
                                    except ValueError:
                                        formatted_numbers.append(f"{num:>20}")
                                formatted_lines.append("    ".join(formatted_numbers))
                            value = "\n\n".join(formatted_lines)
                        values.append(value)
                
                item = self.table.insert("", "end", values=values)
                # Apply alternating row colors
                self.table.item(item, tags=("evenrow" if i % 2 == 0 else "oddrow"))
                    
        except Exception as e:
            self.logger.error(f"Error displaying data: {str(e)}")
            self.table["columns"] = ["Error"]
            self.table.column("Error", anchor="center", width=800)
            self.table.heading("Error", text="Error", anchor="center")
            self.table.insert("", "end", values=(f"Error displaying data: {str(e)}",), tags=('oddrow',))
            
    def display_history(self, history):
        """Display history data in the table."""
        try:
            # Check if widgets still exist
            if not self.table_frame.winfo_exists() or not self.table.winfo_exists():
                return
                
            # Clear existing items
            for item in self.table.get_children():
                self.table.delete(item)
                
            if not history:
                self.table["columns"] = ("Message")
                self.table.column("Message", anchor="center", width=600)
                self.table.heading("Message", text="Message", anchor="center")
                self.table.insert("", "end", values=("No history available",), tags=('oddrow',))
                return
                
            # Configure columns
            columns = ["Function", "Method", "Root", "Date"]
            self.table["columns"] = columns
            
            # Calculate column width based on available space
            available_width = self.table_frame.winfo_width() - self.scrollbar.winfo_width()
            if available_width <= 0:
                available_width = 800  # Default width if not yet available
                
            column_width = max(150, available_width // len(columns))
            
            # Configure columns with calculated width
            for col in columns:
                self.table.column(col, anchor="center", width=column_width)
                self.table.heading(col, text=col, anchor="center")
                
            # Insert data
            for i, entry in enumerate(history):
                try:
                    # Extract and format values
                    function = entry.get("function", "")
                    method = entry.get("method", "")
                    
                    # Format root with proper decimal places
                    root_value = entry.get("root", 0)
                    if isinstance(root_value, (int, float)):
                        root = f"{root_value:.6f}"
                    else:
                        root = str(root_value)
                    
                    # Format date
                    date_str = entry.get("timestamp", "")
                    if date_str:
                        try:
                            from datetime import datetime
                            date_obj = datetime.fromisoformat(date_str)
                            date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                        except (ValueError, TypeError):
                            date = date_str
                    else:
                        date = ""
                    
                    values = [function, method, root, date]
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    self.table.insert("", "end", values=values, tags=(tag,))
                except Exception as row_error:
                    self.logger.error(f"Error processing history row: {str(row_error)}")
                    # Continue with next row even if one fails
                    
        except Exception as e:
            self.logger.error(f"Error displaying history: {str(e)}")
            # Show error message in table
            if self.table.winfo_exists():
                self.table["columns"] = ("Error")
                self.table.column("Error", anchor="center", width=600)
                self.table.heading("Error", text="Error", anchor="center")
                self.table.insert("", "end", values=(f"Error loading history: {str(e)}",), tags=('oddrow',))
    def clear(self):
        """Clear all items from the table."""
        try:
            for item in self.table.get_children():
                self.table.delete(item)
        except Exception as e:
            self.logger.error(f"Error clearing table: {str(e)}")
