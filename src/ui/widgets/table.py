import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import List, Dict, Any, Optional, Union
import logging
import numpy as np
import pandas as pd
import math
from collections import OrderedDict

class ResultTable:
    def __init__(self, parent, theme=None, height=None, width=None, fixed_position=False):
        """
        Initialize the result table.
        
        Args:
            parent: Parent widget
            theme: Theme dictionary
            height: Optional height constraint
            width: Optional width constraint
            fixed_position: Whether to use a fixed position that doesn't expand
        """
        self.theme = theme or {}
        self.logger = logging.getLogger(__name__)
        self.fixed_position = fixed_position
        
        # Create the main frame
        self.table_frame = ctk.CTkFrame(parent, fg_color=self.theme.get("bg", "#F0F4F8"))
        
        # Set up packing or grid based on fixed_position flag
        if fixed_position:
            self.table_frame.pack(fill="both", padx=5, pady=5)
            if height:
                self.table_frame.configure(height=height)
            if width:
                self.table_frame.configure(width=width)
        else:
            self.table_frame.pack(fill="both", expand=True)
        
        # Create a canvas with scrollbar for vertical scrolling
        self.canvas = tk.Canvas(self.table_frame, bg=self.theme.get("bg", "#F0F4F8"), highlightthickness=0)
        self.scrollbar_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.canvas.yview)
        
        # Create a frame for horizontal scrolling if needed
        self.h_scroll_frame = ctk.CTkFrame(self.table_frame, fg_color=self.theme.get("bg", "#F0F4F8"), height=20)
        self.scrollbar_x = ttk.Scrollbar(self.h_scroll_frame, orient="horizontal")
        
        # Create the inner frame that will contain the table
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color=self.theme.get("bg", "#F0F4F8"))
        
        # Configure the canvas scroll region when the frame changes size
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create a window in the canvas for the scrollable frame
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Set up the scrollbar configuration
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar_y.pack(side="right", fill="y")
        
        # Only show horizontal scrollbar when needed
        self.h_scroll_frame.pack(fill="x", expand=False)
        
        # Create the table
        self.table = ttk.Treeview(self.scrollable_frame, style="Custom.Treeview", show="headings", 
                                 selectmode="browse")
        if fixed_position:
            self.table.pack(fill="both")
        else:
            self.table.pack(fill="both", expand=True)
        
        # Configure the horizontal scrollbar for the table
        self.scrollbar_x.config(command=self.table.xview)
        self.table.configure(xscrollcommand=self.scrollbar_x.set)
        
        # Configure hover effect
        hover_color = self.theme.get("table_hover", "#E2E8F0")
        self.table.tag_configure('hover', background=hover_color)
        
        # Configure alternating row colors
        odd_row_color = self.theme.get("table_odd_row", "#F8FAFC")
        even_row_color = self.theme.get("table_even_row", "#FFFFFF")
        self.table.tag_configure('oddrow', background=odd_row_color)
        self.table.tag_configure('evenrow', background=even_row_color)
        
        # Configure special row types
        self.table.tag_configure('info', background="#E6F2FF", foreground="#1E40AF")
        self.table.tag_configure('success', background="#E6F9E6", foreground="#166534")
        self.table.tag_configure('warning', background="#FFF5E6", foreground="#9A3412")
        self.table.tag_configure('error', background="#FFE6E6", foreground="#BE123C")
        self.table.tag_configure('result', background="#F0F9FF", foreground="#0369A1", font=('Helvetica', 10, 'bold'))
        
        # Configure row height and padding for all rows
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=35)  # Increase default row height
        
        # Bind hover events
        self.table.bind('<Motion>', self._on_motion)
        self.table.bind('<Leave>', self._on_leave)
        
        # Set up mousewheel scrolling
        self._setup_mousewheel_scrolling()
        
        # Bind canvas resize event to update window width
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Initialize column sort state
        self.sort_columns = {}  # {column_id: ascending}
        
        # Bind header click for sorting
        self.table.bind("<Button-1>", self._on_header_click)
        
    def _setup_mousewheel_scrolling(self):
        """Set up mousewheel scrolling with cross-platform support."""
        # Store active bindings to be able to unbind them later
        self.active_bindings = []
        
        # Define mousewheel handler
        def _on_mousewheel(event):
            """Handle mousewheel scrolling with cross-platform support."""
            try:
                # Ensure the canvas still exists
                if not self.canvas.winfo_exists():
                    return
                
                # Get current scroll position (for edge detection)
                current_pos = self.canvas.yview()
                
                # Calculate scroll amount based on platform
                scroll_amount = 0
                
                # Windows - uses delta attribute (typically multiples of 120)
                if hasattr(event, "delta"):
                    # Normalize scrolling speed 
                    # Delta is typically 120 on Windows, but we want smoother scrolling
                    scroll_amount = -1 * (event.delta // 120)
                    
                # macOS - uses delta with different values (typically 1 or 2)
                elif hasattr(event, "delta") and abs(event.delta) < 20:
                    scroll_amount = -1 * event.delta
                    
                # Linux - uses Button-4 (up) and Button-5 (down)
                elif hasattr(event, "num"):
                    if event.num == 4:
                        scroll_amount = -1
                    elif event.num == 5:
                        scroll_amount = 1
                    
                # If using a trackpad or other device with natural scrolling
                # Note: Windows with modern touchpads might need additional logic
                
                # Apply the scroll
                if scroll_amount != 0:
                    self.canvas.yview_scroll(int(scroll_amount), "units")
                    
                    # Check if we hit the edge (position didn't change)
                    if self.canvas.yview() == current_pos and scroll_amount != 0:
                        # At edge of scrolling, propagate to parent if needed
                        pass
                    else:
                        # If we scrolled successfully, prevent further propagation
                        return "break"
                        
            except Exception as e:
                # Just log and continue - scroll errors shouldn't disrupt the application
                self.logger.debug(f"Non-critical scroll error: {str(e)}")
                
            # Allow event to propagate if we didn't handle it
            return
            
        # Bind mousewheel events
        def _bind_mousewheel():
            """Bind all mousewheel events for different platforms."""
            try:
                # Windows and macOS
                self.active_bindings.append(self.canvas.bind_all("<MouseWheel>", _on_mousewheel))
                # Linux
                self.active_bindings.append(self.canvas.bind_all("<Button-4>", _on_mousewheel))
                self.active_bindings.append(self.canvas.bind_all("<Button-5>", _on_mousewheel))
                # macOS with trackpad (optional)
                self.active_bindings.append(self.canvas.bind_all("<MouseWheelEvent>", _on_mousewheel))
            except Exception as e:
                self.logger.error(f"Error binding mousewheel: {str(e)}")
                
        # Unbind mousewheel events
        def _unbind_mousewheel():
            """Safely unbind all mousewheel events."""
            try:
                # Check if canvas still exists
                if self.canvas.winfo_exists():
                    self.canvas.unbind_all("<MouseWheel>")
                    self.canvas.unbind_all("<Button-4>")
                    self.canvas.unbind_all("<Button-5>")
                    self.canvas.unbind_all("<MouseWheelEvent>")
            except Exception:
                # Just continue if there's an error
                pass
                
        # Bind the mousewheel events when mouse enters the canvas
        self.canvas.bind("<Enter>", lambda e: _bind_mousewheel())
        self.scrollbar_y.bind("<Enter>", lambda e: _bind_mousewheel())
        self.table.bind("<Enter>", lambda e: _bind_mousewheel())
        
        # Unbind when mouse leaves to avoid interfering with other scrollable areas
        self.canvas.bind("<Leave>", lambda e: _unbind_mousewheel())
        self.scrollbar_y.bind("<Leave>", lambda e: _unbind_mousewheel())
        self.table.bind("<Leave>", lambda e: _unbind_mousewheel())
        
        # Initial binding (optional, can be enabled if you want scrolling to work immediately)
        _bind_mousewheel()
        
    def _on_canvas_resize(self, event):
        """Update canvas window width when canvas is resized."""
        try:
            self.canvas.itemconfig(self.canvas_window, width=event.width)
            
            # If all columns fit, hide horizontal scrollbar
            table_width = sum(int(self.table.column(col, "width")) for col in self.table["columns"])
            if table_width <= event.width:
                self.scrollbar_x.pack_forget()
                self.h_scroll_frame.configure(height=0)
            else:
                self.scrollbar_x.pack(side="bottom", fill="x")
                self.h_scroll_frame.configure(height=20)
        except Exception as e:
            self.logger.error(f"Error resizing canvas: {str(e)}")
            
    def _on_motion(self, event):
        """Handle mouse motion over the table."""
        try:
            item = self.table.identify_row(event.y)
            if item:
                # Get current tags
                tags = list(self.table.item(item, "tags"))
                
                # Skip special rows
                if any(tag in tags for tag in ['info', 'success', 'warning', 'error', 'result']):
                    return
                    
                # Add hover tag if not already present
                if 'hover' not in tags:
                    self.table.item(item, tags=tags + ['hover'])
                    
                # Remove hover from all other items
                for other_item in self.table.get_children():
                    if other_item != item and 'hover' in self.table.item(other_item, "tags"):
                        other_tags = list(self.table.item(other_item, "tags"))
                        other_tags.remove('hover')
                        self.table.item(other_item, tags=other_tags)
        except Exception as e:
            self.logger.error(f"Error in hover effect: {str(e)}")
            
    def _on_leave(self, event):
        """Handle mouse leaving the table."""
        try:
            for item in self.table.get_children():
                tags = list(self.table.item(item, "tags"))
                if 'hover' in tags:
                    tags.remove('hover')
                    self.table.item(item, tags=tags)
        except Exception as e:
            self.logger.error(f"Error in hover leave: {str(e)}")
            
    def _on_header_click(self, event):
        """Handle header click for sorting."""
        try:
            region = self.table.identify_region(event.x, event.y)
            if region == "heading":
                column = self.table.identify_column(event.x)
                column_id = self.table["columns"][int(column.replace('#', '')) - 1]
                
                # Toggle sort order for this column
                ascending = not self.sort_columns.get(column_id, True)
                self.sort_columns = {column_id: ascending}  # Reset other columns
                
                # Get all items
                data = []
                for item in self.table.get_children():
                    values = self.table.item(item, "values")
                    tags = self.table.item(item, "tags")
                    data.append((values, tags))
                
                # Remove all items
                for item in self.table.get_children():
                    self.table.delete(item)
                
                # Sort data by the selected column
                col_idx = self.table["columns"].index(column_id)
                
                # Sort preserving special rows
                special_rows = []
                numeric_rows = []
                text_rows = []
                
                for values, tags in data:
                    if any(tag in tags for tag in ['info', 'success', 'warning', 'error', 'result']):
                        special_rows.append((values, tags))
                    else:
                        # Try to determine if value is numeric
                        value = values[col_idx] if col_idx < len(values) else ""
                        try:
                            # Remove any % or other non-numeric characters
                            clean_value = value.replace('%', '').strip() if isinstance(value, str) else value
                            num_value = float(clean_value)
                            numeric_rows.append((values, tags, num_value))
                        except (ValueError, TypeError):
                            text_rows.append((values, tags, str(value).lower()))
                
                # Sort numeric and text rows separately
                numeric_rows.sort(key=lambda x: x[2], reverse=not ascending)
                text_rows.sort(key=lambda x: x[2], reverse=not ascending)
                
                # Add back in sorted order: numeric, text, special
                for values, tags, _ in numeric_rows:
                    item = self.table.insert("", "end", values=values)
                    self.table.item(item, tags=tags)
                    
                for values, tags, _ in text_rows:
                    item = self.table.insert("", "end", values=values)
                    self.table.item(item, tags=tags)
                    
                for values, tags in special_rows:
                    item = self.table.insert("", "end", values=values)
                    self.table.item(item, tags=tags)
                
                # Update column headers to show sort direction
                for col in self.table["columns"]:
                    if col == column_id:
                        direction = "↑" if ascending else "↓"
                        self.table.heading(col, text=f"{col} {direction}")
                    else:
                        # Remove sort indicator from other columns
                        current_text = self.table.heading(col, "text")
                        clean_text = current_text.split(" ")[0] if " " in current_text else current_text
                        self.table.heading(col, text=clean_text)
        except Exception as e:
            self.logger.error(f"Error sorting table: {str(e)}")

    def update_theme(self, theme):
        """Update the table theme colors."""
        try:
            # Check if widgets still exist
            if not hasattr(self, "table_frame") or not self.table_frame.winfo_exists():
                return
                
            self.theme = theme
            
            # Update frame colors
            self.table_frame.configure(fg_color=self.theme.get("bg", "#F0F4F8"))
            
            if hasattr(self, "canvas") and self.canvas.winfo_exists():
                self.canvas.configure(bg=self.theme.get("bg", "#F0F4F8"))
                
            if hasattr(self, "scrollable_frame") and self.scrollable_frame.winfo_exists():
                self.scrollable_frame.configure(fg_color=self.theme.get("bg", "#F0F4F8"))
            
            if hasattr(self, "h_scroll_frame") and self.h_scroll_frame.winfo_exists():
                self.h_scroll_frame.configure(fg_color=self.theme.get("bg", "#F0F4F8"))
            
            # Update hover and row colors
            hover_color = self.theme.get("table_hover", "#E2E8F0")
            odd_row_color = self.theme.get("table_odd_row", "#F8FAFC")
            even_row_color = self.theme.get("table_even_row", "#FFFFFF")
            
            if hasattr(self, "table") and self.table.winfo_exists():
                self.table.tag_configure('hover', background=hover_color)
                self.table.tag_configure('oddrow', background=odd_row_color)
                self.table.tag_configure('evenrow', background=even_row_color)
                
                # Add tags for special message rows
                self.table.tag_configure('info', background="#E6F2FF", foreground="#1E40AF")
                self.table.tag_configure('success', background="#E6F9E6", foreground="#166534")
                self.table.tag_configure('warning', background="#FFF5E6", foreground="#9A3412")
                self.table.tag_configure('error', background="#FFE6E6", foreground="#BE123C")
                self.table.tag_configure('result', background="#F0F9FF", foreground="#0369A1", font=('Helvetica', 10, 'bold'))
                
                # Update table style while preserving row height
                style = ttk.Style()
                current_rowheight = style.lookup("Custom.Treeview", "rowheight")
                
                style.configure("Custom.Treeview",
                              background=self.theme.get("table_bg", "#F0F4F8"),
                              foreground=self.theme.get("table_fg", "#1E293B"),
                              fieldbackground=self.theme.get("table_bg", "#F0F4F8"),
                              rowheight=current_rowheight or 35)  # Maintain current row height or use default
                
                style.configure("Custom.Treeview.Heading",
                              background=self.theme.get("table_heading_bg", "#E2E8F0"),
                              foreground=self.theme.get("table_heading_fg", "#1E293B"))
                
                # Reapply row colors to existing rows
                for idx, item in enumerate(self.table.get_children()):
                    # Get current tags
                    tags = list(self.table.item(item, "tags"))
                    
                    # Filter out row coloring tags
                    tags = [tag for tag in tags if tag not in ('oddrow', 'evenrow')]
                    
                    # Add appropriate row tag
                    if "info" in tags or "warning" in tags or "error" in tags or "success" in tags or "result" in tags:
                        # Preserve special row tags
                        pass
                    else:
                        # Add row coloring
                        if idx % 2 == 0:
                            tags.append('evenrow')
                        else:
                            tags.append('oddrow')
                    
                    # Update tags
                    self.table.item(item, tags=tags)
            
        except Exception as e:
            self.logger.error(f"Error updating table theme: {str(e)}")

    def _format_value(self, value, decimal_places=4):
        """Format a value for display."""
        try:
            # Check for special types
            if isinstance(value, np.ndarray):
                return self._format_matrix(value, decimal_places)
                
            if isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                return self._format_vector(value, decimal_places)
                
            # Check for numeric types
            if isinstance(value, (int, float)):
                if math.isnan(value):
                    return "NaN"
                elif math.isinf(value):
                    return "Inf" if value > 0 else "-Inf"
                elif value == int(value):
                    return str(int(value))
                else:
                    return f"{value:.{decimal_places}f}"
                    
            # Default: convert to string
            return str(value)
        except Exception as e:
            self.logger.error(f"Error formatting value: {str(e)}")
            return str(value)

    def _format_matrix(self, matrix: np.ndarray, decimal_places: int) -> str:
        """Format a matrix for display in a cell."""
        try:
            if matrix.ndim == 2:
                rows = []
                for row in matrix:
                    formatted_row = '[ '  # Added space after bracket
                    row_values = []
                    for x in row:
                        if isinstance(x, (int, float)):
                            if math.isnan(x):
                                row_values.append("NaN")
                            elif math.isinf(x):
                                row_values.append("Inf" if x > 0 else "-Inf")
                            else:
                                row_values.append(f"{x:.{decimal_places}f}")
                        else:
                            row_values.append(str(x))
                    formatted_row += ' ,  '.join(row_values) + ' ]'  # Added more spacing
                    rows.append(formatted_row)
                return '[\n  ' + '\n  '.join(rows) + '\n]'  # Return with newlines for better readability
            else:
                return self._format_vector(matrix, decimal_places)
        except Exception as e:
            self.logger.error(f"Error formatting matrix: {str(e)}")
            return str(matrix)

    def _format_vector(self, vector: Union[np.ndarray, List], decimal_places: int) -> str:
        """Format a vector for display in a cell."""
        try:
            formatted_values = []
            for x in vector:
                if isinstance(x, (int, float)):
                    if math.isnan(x):
                        formatted_values.append("NaN")
                    elif math.isinf(x):
                        formatted_values.append("Inf" if x > 0 else "-Inf")
                    else:
                        formatted_values.append(f"{x:.{decimal_places}f}")
                else:
                    formatted_values.append(str(x))
            return '[ ' + ' ,  '.join(formatted_values) + ' ]'  # Added more spacing
        except Exception as e:
            self.logger.error(f"Error formatting vector: {str(e)}")
            return str(vector)

    def display(self, data):
        """
        Display data in the table.
        
        Args:
            data: List of dictionaries or Pandas DataFrame
        """
        try:
            # Clear existing data
            self.clear()
            
            # Handle different data types
            if isinstance(data, pd.DataFrame):
                df_data = data
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # For OrderedDict or regular dict, preserve the order of columns
                # from the first row, which is crucial for Fixed Point and other methods
                df_data = pd.DataFrame(data)
                # Preserve the original order of columns if it was an OrderedDict
                if isinstance(data[0], OrderedDict):
                    df_data = df_data[list(data[0].keys())]
            elif isinstance(data, dict):
                df_data = pd.DataFrame([data])
            else:
                self.logger.error(f"Unsupported data type: {type(data)}")
                # Display error message
                self.table["columns"] = ["Error"]
                self.table.column("Error", width=400, anchor="center")
                self.table.heading("Error", text="Error")
                self.table.insert("", "end", values=["Unsupported data format"], tags=("error",))
                return

            # Configure columns
            column_ids = list(df_data.columns)
            self.table["columns"] = column_ids
            
            # Set column widths and headings
            for col in column_ids:
                width = 150  # Default width
                
                # Adjust width based on column type and header length
                col_str = str(col)
                header_width = len(col_str) * 10
                
                # Increase width for columns that might contain longer values
                if col in ["xi", "g(xi)"]:
                    width = 250  # Wider for these columns
                elif col in ["Error %"]:
                    width = 120  # Error column can be narrower
                elif col in ["Iteration"]:
                    width = 100  # Iteration column can be narrower
                
                # Adjust width based on content length
                col_values = df_data[col].astype(str)
                if not col_values.empty:
                    # Check for long content and make those columns wider
                    max_content_width = col_values.str.len().max() * 8
                    width = max(width, header_width, min(max_content_width, 400))
                else:
                    width = max(width, header_width)
                
                self.table.column(col, width=width, minwidth=100, anchor="center")
                self.table.heading(col, text=col_str, anchor="center")
            
            # Check if we need to use different row heights for matrix displays
            contains_matrix = False
            for col in column_ids:
                # Check a sample of values from the column
                sample_values = df_data[col].astype(str).sample(min(5, len(df_data)))
                for val in sample_values:
                    if isinstance(val, str) and '\n' in val:
                        contains_matrix = True
                        break
                if contains_matrix:
                    break
            
            # If matrix data is detected, configure a larger row height
            if contains_matrix:
                style = ttk.Style()
                style.configure("Custom.Treeview", rowheight=90)  # Increased from 70 to 90 for matrices
            
            # Iterate through each row
            for idx, row in df_data.iterrows():
                values = []
                
                # Format each value
                for col in column_ids:
                    value = row[col]
                    values.append(self._format_value(value))
                
                # Insert row with appropriate tag
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                
                # Check for special message rows
                if "Iteration" in row:
                    iteration = row["Iteration"]
                    if iteration == "Error":
                        tag = "error"
                    elif iteration == "Warning":
                        tag = "warning"
                    elif iteration == "Info":
                        tag = "info"
                    elif iteration == "Result":
                        tag = "result"
                    elif iteration == "Success":
                        tag = "success"
                
                self.table.insert("", "end", values=values, tags=(tag,))
                
            # Show horizontal scrollbar if needed
            table_width = sum(int(self.table.column(col, "width")) for col in column_ids)
            canvas_width = self.canvas.winfo_width()
            
            if table_width > canvas_width:
                self.scrollbar_x.pack(side="bottom", fill="x")
                self.h_scroll_frame.configure(height=20)
            else:
                self.scrollbar_x.pack_forget()
                self.h_scroll_frame.configure(height=0)
                
        except Exception as e:
            self.logger.error(f"Error displaying data: {str(e)}")
            # Display error message
            self.clear()
            self.table["columns"] = ["Error"]
            self.table.column("Error", width=400, anchor="center")
            self.table.heading("Error", text="Error")
            self.table.insert("", "end", values=[f"Error displaying data: {str(e)}"], tags=("error",))

    def display_history(self, history):
        """
        Display history entries in the table.
        
        Args:
            history: List of history entries
        """
        try:
            # Clear existing data
            self.clear()
            
            if not history or len(history) == 0:
                # Display message for empty history
                self.table["columns"] = ["Info"]
                self.table.column("Info", width=400, anchor="center")
                self.table.heading("Info", text="Information")
                self.table.insert("", "end", values=["No history entries found"], tags=("info",))
                return
            
            # Configure columns
            columns = ["Index", "Date", "Time", "Method", "Function", "Root", "Tags"]
            self.table["columns"] = columns
            
            # Set column widths and headings
            col_widths = {
                "Index": 60,
                "Date": 100,
                "Time": 100,
                "Method": 150,
                "Function": 250,
                "Root": 150,
                "Tags": 150
            }
            
            for col in columns:
                width = col_widths.get(col, 150)
                self.table.column(col, width=width, minwidth=60, anchor="center")
                self.table.heading(col, text=col, anchor="center")
            
            # Insert history entries
            for idx, entry in enumerate(history):
                # Format root value(s)
                root = entry.get("root", "")
                if isinstance(root, list):
                    root_str = ", ".join([str(r) for r in root if r is not None])
                else:
                    root_str = str(root)
                
                # Format tags
                tags = entry.get("tags", [])
                tags_str = ", ".join(tags) if tags else ""
                
                # Prepare row values
                values = [
                    idx,
                    entry.get("date", ""),
                    entry.get("time", ""),
                    entry.get("method", ""),
                    entry.get("function", ""),
                    root_str,
                    tags_str
                ]
                
                # Insert with alternating row colors
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.table.insert("", "end", values=values, tags=(tag,))
                
            # Show horizontal scrollbar if needed
            table_width = sum(int(self.table.column(col, "width")) for col in columns)
            canvas_width = self.canvas.winfo_width()
            
            if table_width > canvas_width:
                self.scrollbar_x.pack(side="bottom", fill="x")
                self.h_scroll_frame.configure(height=20)
            else:
                self.scrollbar_x.pack_forget()
                self.h_scroll_frame.configure(height=0)
                
        except Exception as e:
            self.logger.error(f"Error displaying history: {str(e)}")
            # Display error message
            self.clear()
            self.table["columns"] = ["Error"]
            self.table.column("Error", width=400, anchor="center")
            self.table.heading("Error", text="Error")
            self.table.insert("", "end", values=[f"Error displaying history: {str(e)}"], tags=("error",))

    def clear(self):
        """Clear the table."""
        try:
            # Check if the table exists
            if hasattr(self, "table") and self.table.winfo_exists():
                # Delete all items
                for item in self.table.get_children():
                    self.table.delete(item)
                    
                # Reset columns
                self.table["columns"] = []
                
                # Reset sort state
                self.sort_columns = {}
        except Exception as e:
            self.logger.error(f"Error clearing table: {str(e)}")
            
    def get_selected_row(self):
        """
        Get the selected row data.
        
        Returns:
            Dict with column names and values
        """
        try:
            selected_items = self.table.selection()
            if not selected_items:
                return None
                
            # Get the first selected item
            item = selected_items[0]
            
            # Get values and column names
            values = self.table.item(item, "values")
            columns = self.table["columns"]
            
            # Create a dictionary
            return {columns[i]: values[i] for i in range(min(len(columns), len(values)))}
            
        except Exception as e:
            self.logger.error(f"Error getting selected row: {str(e)}")
            return None
            
    def export_to_csv(self, filename: str):
        """
        Export table data to CSV.
        
        Args:
            filename: CSV file path
            
        Returns:
            bool: True if successful
        """
        try:
            # Get column names
            columns = self.table["columns"]
            if not columns:
                return False
                
            # Get all rows
            rows = []
            for item in self.table.get_children():
                values = self.table.item(item, "values")
                row_dict = {columns[i]: values[i] for i in range(min(len(columns), len(values)))}
                rows.append(row_dict)
                
            # Create DataFrame and save to CSV
            df = pd.DataFrame(rows)
            df.to_csv(filename, index=False)
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            return False
