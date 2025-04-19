import customtkinter as ctk
from tkinter import ttk
from src.ui.widgets.input_form import InputForm
from src.ui.widgets.table import ResultTable
from src.ui.widgets.sidebar import Sidebar
from src.core.solver import Solver
from src.core.history import HistoryManager
from src.ui.theme import ThemeManager
from src.utils.export import export_to_pdf
import logging

class NumericalApp:
    def __init__(self):
        """Initialize the application."""
        self.root = ctk.CTk()
        self.root.title("Numerical Analysis App")
        self.root.geometry("1000x700")
        self.logger = logging.getLogger(__name__)
        self.version = "1.0.0"  # Add version attribute
        
        try:
            self.theme_manager = ThemeManager()
            self.history_manager = HistoryManager()
            self.solver = Solver()
            self.theme = self.theme_manager.apply_theme()
            self.configure_table_style()
            self.setup_welcome_screen()
        except Exception as e:
            self.logger.error(f"Error initializing app: {str(e)}")
            raise

    def configure_table_style(self):
        """Configure the table style for better visibility."""
        try:
            style = ttk.Style()
            
            # Configure the main table style
            style.configure("Custom.Treeview",
                          background=self.theme["table_bg"],
                          foreground=self.theme["table_fg"],
                          fieldbackground=self.theme["table_bg"],
                          rowheight=25)
            
            # Configure the table heading style
            style.configure("Custom.Treeview.Heading",
                          background=self.theme["table_heading_bg"],
                          foreground=self.theme["table_heading_fg"],
                          font=("Helvetica", 10, "bold"))
            
            # Configure selection colors
            style.map("Custom.Treeview",
                     background=[("selected", self.theme["button"])],
                     foreground=[("selected", self.theme["text"])])
            
            # Configure row colors
            style.map("Custom.Treeview",
                     background=[("selected", self.theme["button"])],
                     foreground=[("selected", self.theme["text"])])
            
            self.logger.info("Table style configured successfully")
        except Exception as e:
            self.logger.error(f"Error configuring table style: {str(e)}")

    def setup_welcome_screen(self):
        """Initialize and display the welcome screen."""
        try:
            self.welcome_frame = ctk.CTkFrame(self.root, fg_color=self.theme["bg"])
            self.welcome_frame.pack(fill="both", expand=True)
            
            # Create a container for welcome content
            welcome_container = ctk.CTkFrame(self.welcome_frame, fg_color=self.theme["bg"])
            welcome_container.pack(expand=True)
            
            # Add application title
            title_label = ctk.CTkLabel(
                welcome_container, 
                text="Numerical Analysis App", 
                font=("Helvetica", 48, "bold"), 
                text_color=self.theme["accent"]
            )
            title_label.pack(pady=(0, 20))
            
            # Add version info
            version_label = ctk.CTkLabel(
                welcome_container, 
                text=f"Version {self.version}", 
                font=("Helvetica", 16), 
                text_color=self.theme["text"]
            )
            version_label.pack(pady=(0, 40))
            
            # Add loading indicator
            loading_label = ctk.CTkLabel(
                welcome_container, 
                text="Loading...", 
                font=("Helvetica", 14), 
                text_color=self.theme["text"]
            )
            loading_label.pack()
            
            # Schedule transition to main window
            self.root.after(2000, self.show_main_window)
            
        except Exception as e:
            self.logger.error(f"Error setting up welcome screen: {str(e)}")
            raise

    def show_main_window(self):
        """Transition from welcome screen to main window."""
        try:
            # Destroy welcome frame if it exists
            if hasattr(self, "welcome_frame") and self.welcome_frame.winfo_exists():
                self.welcome_frame.destroy()
            
            # Create main frame
            self.main_frame = ctk.CTkFrame(self.root, fg_color=self.theme["bg"])
            self.main_frame.pack(fill="both", expand=True)

            # Create header
            self.header = ctk.CTkFrame(self.main_frame, height=60, fg_color=self.theme["fg"])
            self.header.pack(fill="x", pady=(0, 10))
            
            # Add title to header
            ctk.CTkLabel(
                self.header, 
                text="Numerical Analysis", 
                font=("Helvetica", 24, "bold"), 
                text_color=self.theme["accent"]
            ).pack(side="left", padx=20)
            
            # Add theme selector
            theme_menu = ctk.CTkOptionMenu(
                self.header, 
                values=list(self.theme_manager.themes.keys()), 
                command=self.change_theme, 
                fg_color=self.theme["button"], 
                button_color=self.theme["button_hover"], 
                button_hover_color=self.theme["accent"]
            )
            theme_menu.pack(side="right", padx=20)

            # Create sidebar
            self.sidebar = Sidebar(
                self.main_frame, 
                self.theme, 
                self.show_home, 
                self.show_history, 
                self.show_settings, 
                self.show_about
            )
            
            # Create content frame
            self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=self.theme["bg"])
            self.content_frame.pack(side="left", fill="both", expand=True)
            
            # Show home screen
            self.show_home()
            
        except Exception as e:
            self.logger.error(f"Error showing main window: {str(e)}")
            raise

    def change_theme(self, theme_name: str):
        self.theme = self.theme_manager.set_theme(theme_name)
        self.update_ui_theme()

    def update_ui_theme(self):
        """Update UI elements with the current theme."""
        try:
            # Update the main window background
            self.root.configure(fg_color=self.theme.get("bg", "#F0F4F8"))
            
            # Update the sidebar
            if hasattr(self, "sidebar"):
                try:
                    self.sidebar.update_theme(self.theme)
                except Exception as sidebar_error:
                    self.logger.error(f"Error updating sidebar theme: {str(sidebar_error)}")
            
            # Update tables if they exist
            if hasattr(self, "result_table") and self.result_table is not None:
                try:
                    self.result_table.update_theme(self.theme)
                except Exception as table_error:
                    self.logger.error(f"Error updating result table theme: {str(table_error)}")
                    
            if hasattr(self, "history_table") and self.history_table is not None:
                try:
                    self.history_table.update_theme(self.theme)
                except Exception as table_error:
                    self.logger.error(f"Error updating history table theme: {str(table_error)}")
                    
            # Update forms if they exist
            if hasattr(self, "input_form") and self.input_form is not None:
                try:
                    self.input_form.update_theme(self.theme)
                except Exception as form_error:
                    self.logger.error(f"Error updating input form theme: {str(form_error)}")
                
            # Configure the Table Style
            self.configure_table_style()
                
        except Exception as e:
            self.logger.error(f"Error updating UI theme: {str(e)}")

    def show_home(self):
        """Display the home screen with input form and results table."""
        try:
            self.clear_content()
            
            # Create a canvas and scrollbar for scrolling
            canvas = ctk.CTkCanvas(self.content_frame, bg=self.theme.get("bg", "#F0F4F8"), highlightthickness=0)
            scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
            
            # Create the main frame that will be scrolled
            home_frame = ctk.CTkFrame(canvas, fg_color=self.theme.get("bg", "#F0F4F8"))
            
            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack the scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Create a window in the canvas for the frame
            canvas_window = canvas.create_window((0, 0), window=home_frame, anchor="nw", width=canvas.winfo_width())
            
            # Update the scroll region when the frame changes size
            def configure_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            home_frame.bind("<Configure>", configure_scroll_region)
            
            # Update the canvas window width when the canvas is resized
            def configure_canvas_window(event):
                canvas.itemconfig(canvas_window, width=event.width)
            
            canvas.bind("<Configure>", configure_canvas_window)
            
            # Add mousewheel scrolling
            def _on_mousewheel(event):
                """Handle mouse wheel scrolling smoothly across platforms."""
                try:
                    # Check if canvas exists and is valid
                    if not hasattr(event, "widget") or not event.widget.winfo_exists():
                        return
                        
                    # Ensure the canvas still exists
                    if not canvas.winfo_exists():
                        return
                    
                    # Get the current scrollbar position
                    current_pos = canvas.yview()
                    
                    # Calculate scroll amount based on platform
                    scroll_amount = 0
                    
                    # Windows - uses delta attribute (typically multiples of 120)
                    if hasattr(event, "delta") and event.delta != 0:
                        # Normalize delta for smoother scrolling
                        scroll_amount = -1 * (event.delta // 120)
                    
                    # macOS - uses delta with different values
                    elif hasattr(event, "delta") and abs(event.delta) < 20:
                        scroll_amount = -1 * event.delta
                    
                    # Linux - uses num attribute (4 is up, 5 is down)
                    elif hasattr(event, "num"):
                        if event.num == 4:
                            scroll_amount = -1
                        elif event.num == 5:
                            scroll_amount = 1
                    
                    # Apply the scroll if we determined an amount
                    if scroll_amount != 0:
                        canvas.yview_scroll(int(scroll_amount), "units")
                        
                        # Check if the view actually changed (if not, we're at the beginning or end)
                        new_pos = canvas.yview()
                        if new_pos == current_pos and scroll_amount != 0:
                            # At edge of scrolling, let the parent handle it if needed
                            pass
                        else:
                            # Prevent further propagation if we scrolled successfully
                            return "break"
                except Exception as e:
                    # Log the error but don't disrupt the user experience
                    self.logger.debug(f"Scroll error (non-critical): {str(e)}")
                
                # Allow event to propagate if we didn't handle it
                return
            
            # Reference to store active bindings
            self.active_bindings = []
            
            # Bind mousewheel events safely
            def _bind_mousewheel():
                """Bind all mousewheel events for different platforms."""
                try:
                    # Windows and macOS standard wheel
                    self.active_bindings.append(canvas.bind_all("<MouseWheel>", _on_mousewheel))
                    # Linux wheel
                    self.active_bindings.append(canvas.bind_all("<Button-4>", _on_mousewheel))
                    self.active_bindings.append(canvas.bind_all("<Button-5>", _on_mousewheel))
                    # macOS with trackpad
                    self.active_bindings.append(canvas.bind_all("<MouseWheelEvent>", _on_mousewheel))
                except Exception as e:
                    self.logger.error(f"Error binding mousewheel: {str(e)}")
            
            # Unbind mousewheel events safely
            def _unbind_mousewheel():
                try:
                    if canvas.winfo_exists():
                        canvas.unbind_all("<MouseWheel>")
                        canvas.unbind_all("<Button-4>")
                        canvas.unbind_all("<Button-5>")
                        canvas.unbind_all("<MouseWheelEvent>")
                except Exception:
                    # Silent failure for unbinding
                    pass
            
            # Initial binding
            _bind_mousewheel()
            
            # Bind/unbind on enter/leave
            canvas.bind("<Enter>", lambda e: _bind_mousewheel())
            canvas.bind("<Leave>", lambda e: _unbind_mousewheel())
            home_frame.bind("<Enter>", lambda e: _bind_mousewheel())
            home_frame.bind("<Leave>", lambda e: _unbind_mousewheel())
            
            # Create a label for the home screen
            home_label = ctk.CTkLabel(
                home_frame,
                text="Numerical Analysis Calculator",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=self.theme.get("text", "#1E293B")
            )
            home_label.pack(pady=(10, 10))
            
            # Create the input form with the correct parameters
            from src.ui.widgets.input_form import InputForm
            self.input_form = InputForm(
                home_frame, 
                self.theme, 
                list(self.solver.methods.keys()), 
                self.solve
            )
            self.input_form.frame.pack(fill="x", padx=10, pady=10)
            
            # Create layout containers
            main_content = ctk.CTkFrame(home_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            main_content.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Create a container frame for the table that fills most of the screen
            table_container = ctk.CTkFrame(main_content, fg_color=self.theme.get("bg", "#F0F4F8"), height=450)
            table_container.pack(fill="both", expand=True, side="top", padx=5, pady=5)
            table_container.pack_propagate(False)  # Prevent container from resizing
            
            # Create the results table with fixed_position=True
            self.result_table = ResultTable(table_container, self.theme, height=450, fixed_position=True)
            self.result_table.table_frame.pack(fill="both", expand=True)
            
            # Create a label for displaying the result
            self.result_label = ctk.CTkLabel(
                main_content,
                text="",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.theme.get("primary", "#3B82F6")
            )
            self.result_label.pack(pady=10)
            
            # Add a frame for the plot with sufficient height
            self.plot_frame = ctk.CTkFrame(main_content, fg_color=self.theme.get("bg", "#F0F4F8"), height=350)
            self.plot_frame.pack(fill="both", expand=True, padx=5, pady=10)
            self.plot_frame.pack_propagate(False)  # Prevent plot frame from shrinking
            
            # Add a placeholder label for the plot
            self.plot_label = ctk.CTkLabel(
                self.plot_frame,
                text="Function plot will appear here after solving",
                font=ctk.CTkFont(size=14),
                text_color=self.theme.get("text", "#1E293B")
            )
            self.plot_label.pack(pady=20)
            
            # Handle plot frame mouse events
            self.plot_frame.bind("<Enter>", lambda e: _unbind_mousewheel())
            self.plot_frame.bind("<Leave>", lambda e: _bind_mousewheel())
            
            # Add buttons container
            buttons_frame = ctk.CTkFrame(home_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            buttons_frame.pack(fill="x", padx=10, pady=5)
            
            # Add an export button
            export_button = ctk.CTkButton(
                buttons_frame,
                text="Export to PDF",
                command=self.export_solution,
                fg_color=self.theme.get("button", "#3B82F6"),
                hover_color=self.theme.get("button_hover", "#2563EB"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            export_button.pack(side="left", padx=10, pady=10, expand=True)
            
        except Exception as e:
            self.logger.error(f"Error showing home screen: {str(e)}")
            # Create a basic error display if the home frame creation fails
            error_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            error_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"Error loading home screen: {str(e)}",
                text_color="red",
                font=ctk.CTkFont(size=14)
            )
            error_label.pack(pady=10)

    def solve(self, **kwargs):
        """
        Solve the problem using the selected method
        
        Args:
            **kwargs: Keyword arguments including:
                - f_str: The function as a string
                - method: The method name
                - params: Additional parameters for the method
                - eps: Error tolerance
                - eps_operator: Comparison operator for epsilon check
                - max_iter: Maximum iterations
                - stop_by_eps: Whether to stop by epsilon
                - decimal_places: Number of decimal places for rounding
        """
        try:
            # Clear previous results
            if hasattr(self, 'result_label'):
                self.result_label.configure(text="")
            
            # Clear previous plot
            if hasattr(self, 'plot_frame'):
                # Remove any existing plot widgets
                for widget in self.plot_frame.winfo_children():
                    try:
                        widget.destroy()
                    except Exception:
                        pass
                
                # Add a placeholder label
                self.plot_label = ctk.CTkLabel(
                    self.plot_frame,
                    text="Solving...",
                    font=ctk.CTkFont(size=14),
                    text_color=self.theme.get("text", "#1E293B")
                )
                self.plot_label.pack(pady=20)
                self.plot_frame.update()  # Force update to show the label
            
            # Extract parameters from kwargs
            f_str = kwargs.get('f_str', '')
            method = kwargs.get('method', '')
            params = kwargs.get('params', {})
            eps = kwargs.get('eps', None)
            eps_operator = kwargs.get('eps_operator', "<=")
            max_iter = kwargs.get('max_iter', None)
            stop_by_eps = kwargs.get('stop_by_eps', None)
            decimal_places = kwargs.get('decimal_places', None)
            
            # Solve the problem
            result, table_data = self.solver.solve(method, f_str, params, eps, eps_operator, max_iter, stop_by_eps, decimal_places)
            
            if hasattr(self, 'result_table'):
                # Display the result in the table
                self.result_table.display(table_data)
                
                # Display the result
                if hasattr(self, 'result_label'):
                    # Get root value (handle different result types) and display it
                    root_message = "No solution found"
                    if result is not None:
                        if hasattr(result, 'root') and result.root is not None:
                            # Object with 'root' attribute (like FixedPointResult)
                            root_message = f"Root found: {result.root}"
                            # Include status if available
                            if hasattr(result, 'status') and result.status:
                                root_message += f" (Status: {result.status})"
                        elif isinstance(result, (int, float)):
                            # Direct numeric result
                            root_message = f"Root found: {result}"
                        elif isinstance(result, tuple) and len(result) > 0:
                            # Tuple with root as first element (like in Bisection, False Position, etc.)
                            if result[0] is not None and isinstance(result[0], (int, float)):
                                root_message = f"Root found: {result[0]}"
                        
                        # Look for Status information in the table data for methods that return it
                        method_status = None
                        for row in table_data:
                            if isinstance(row, dict) and "Status" in row:
                                method_status = row.get("Status")
                                if method_status and method_status not in ["Finding root...", "Completed"]:
                                    # Found a meaningful status in the results
                                    if "Root found" in root_message:
                                        root_message += f" (Status: {method_status})"
                                    else:
                                        root_message = f"Status: {method_status}"
                                    break
                    
                    self.result_label.configure(text=root_message)
                
                # Try to create a plot if we have a function
                if hasattr(self, 'plot_frame'):
                    # Clear the placeholder
                    for widget in self.plot_frame.winfo_children():
                        try:
                            widget.destroy()
                        except Exception:
                            pass
                    
                    # Get root value (handle different result types)
                    root_value = None
                    if result:
                        if hasattr(result, 'root'):
                            root_value = result.root
                        elif isinstance(result, (int, float)):
                            root_value = result
                        elif isinstance(result, tuple) and len(result) > 0 and isinstance(result[0], (int, float)):
                            root_value = result[0]
                    
                    # Get the function string if available and we have a root
                    if f_str and f_str != "System of Linear Equations" and root_value is not None:
                        try:
                            # Log before attempting to create plot
                            self.logger.info(f"Attempting to create plot for function: {f_str} with root: {root_value}")
                            
                            import matplotlib.pyplot as plt
                            import numpy as np
                            import sympy as sp
                            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                            
                            # Create and solve the function
                            x = sp.Symbol('x')
                            f = sp.sympify(f_str)
                            f_lambda = sp.lambdify(x, f, 'numpy')
                            
                            # Create a plot around the root
                            root = float(root_value)
                            plot_range = max(4, abs(root) * 2)  # Ensure reasonable plot range
                            x_range = np.linspace(root - plot_range/2, root + plot_range/2, 1000)
                            
                            # Compute function values safely
                            y_values = []
                            x_filtered = []
                            
                            for x_val in x_range:
                                try:
                                    y_val = f_lambda(x_val)
                                    # Check if the result is a valid number
                                    if np.isfinite(y_val) and not np.isnan(y_val):
                                        y_values.append(y_val)
                                        x_filtered.append(x_val)
                                except Exception:
                                    pass
                            
                            if len(x_filtered) > 0 and len(y_values) > 0:
                                # Create the plot
                                fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
                                ax.plot(x_filtered, y_values, 'b-', label=f'f(x) = {f_str}')
                                
                                # Plot the root
                                try:
                                    root_y = f_lambda(root)
                                    if np.isfinite(root_y) and not np.isnan(root_y):
                                        ax.plot(root, root_y, 'ro', label=f'Root: {root:.6f}', markersize=8)
                                except Exception:
                                    pass
                                
                                # Extract iteration points from the table data if available
                                iteration_x = []
                                iteration_y = []
                                
                                try:
                                    # Handle data based on the method
                                    if method == "Bisection Method":
                                        # Extract data from the table
                                        for row in table_data:
                                            if isinstance(row, dict) and "Iteration" in row and "Xr" in row:
                                                if isinstance(row["Iteration"], int):  # Only plot numerical iterations
                                                    x_val = float(row["Xr"])
                                                    try:
                                                        y_val = f_lambda(x_val)
                                                        if np.isfinite(y_val) and not np.isnan(y_val):
                                                            iteration_x.append(x_val)
                                                            iteration_y.append(y_val)
                                                    except Exception:
                                                        pass
                                    
                                    elif method == "False Position Method":
                                        # Extract data from the table
                                        for row in table_data:
                                            if isinstance(row, dict) and "Iteration" in row and "Xr" in row:
                                                if isinstance(row["Iteration"], int):  # Only plot numerical iterations
                                                    x_val = float(row["Xr"])
                                                    try:
                                                        y_val = f_lambda(x_val)
                                                        if np.isfinite(y_val) and not np.isnan(y_val):
                                                            iteration_x.append(x_val)
                                                            iteration_y.append(y_val)
                                                    except Exception:
                                                        pass
                                    
                                    elif method == "Secant Method":
                                        # Extract data from the table
                                        for row in table_data:
                                            if isinstance(row, dict) and "Iteration" in row and "Xi+1" in row:
                                                if isinstance(row["Iteration"], int):  # Only plot numerical iterations
                                                    x_val = float(row["Xi+1"])
                                                    try:
                                                        y_val = f_lambda(x_val)
                                                        if np.isfinite(y_val) and not np.isnan(y_val):
                                                            iteration_x.append(x_val)
                                                            iteration_y.append(y_val)
                                                    except Exception:
                                                        pass
                                    
                                    elif method == "Fixed Point Method":
                                        # Extract data from the table
                                        for row in table_data:
                                            if isinstance(row, dict) and "Iteration" in row and "xi" in row:
                                                if isinstance(row["Iteration"], int):  # Only plot numerical iterations
                                                    x_val = float(row["xi"])
                                                    try:
                                                        y_val = f_lambda(x_val)
                                                        if np.isfinite(y_val) and not np.isnan(y_val):
                                                            iteration_x.append(x_val)
                                                            iteration_y.append(y_val)
                                                    except Exception:
                                                        pass
                                    
                                    # Plot iteration points if available
                                    if iteration_x and iteration_y:
                                        # Plot iteration points with connecting line to show convergence path
                                        ax.plot(iteration_x, iteration_y, 'g--o', label='Iteration Points', 
                                                alpha=0.7, markersize=6, markerfacecolor='white')
                                        
                                        # Annotate the first few points with iteration numbers
                                        max_annotations = min(6, len(iteration_x))
                                        for i in range(max_annotations):
                                            ax.annotate(f"{i}", 
                                                       (iteration_x[i], iteration_y[i]),
                                                       textcoords="offset points", 
                                                       xytext=(0,10), 
                                                       ha='center')
                                
                                except Exception as e:
                                    self.logger.warning(f"Error plotting iteration points: {str(e)}")
                                
                                # Add a horizontal line at y=0
                                ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                                
                                # Add labels and grid
                                ax.set_xlabel('x')
                                ax.set_ylabel('f(x)')
                                ax.set_title(f'Plot of f(x) = {f_str}')
                                ax.grid(True, alpha=0.3)
                                ax.legend()
                                
                                # Adjust plot limits to show convergence more clearly
                                if iteration_x and len(iteration_x) > 1:
                                    # Get the range of iteration points
                                    iter_min, iter_max = min(iteration_x), max(iteration_x)
                                    # Extend the range by 20% on each side for better visibility
                                    range_extension = (iter_max - iter_min) * 0.2
                                    # Make sure we include the root
                                    plot_min = min(iter_min - range_extension, root - range_extension)
                                    plot_max = max(iter_max + range_extension, root + range_extension)
                                    # Set the x-axis limits
                                    ax.set_xlim(plot_min, plot_max)
                                
                                # Use FigureCanvasTkAgg
                                plot_frame = ctk.CTkFrame(self.plot_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
                                plot_frame.pack(fill="both", expand=True)
                                
                                canvas = FigureCanvasTkAgg(fig, master=plot_frame)
                                canvas_widget = canvas.get_tk_widget()
                                canvas_widget.pack(fill="both", expand=True)
                                
                                # Draw the canvas
                                canvas.draw()
                                
                                # Store reference to avoid garbage collection
                                self.current_plot = {
                                    'figure': fig,
                                    'canvas': canvas,
                                    'frame': plot_frame
                                }
                                
                                # Log that the plot was successfully created
                                self.logger.info("Plot created successfully")
                            else:
                                self._show_plot_error("Could not generate valid function values for plotting")
                        except Exception as e:
                            self.logger.error(f"Error creating plot: {str(e)}")
                            self._show_plot_error(f"Error creating plot: {str(e)}")
                    else:
                        reason = "No valid function provided" if not f_str or f_str == "System of Linear Equations" else "No root found"
                        self._show_plot_error(f"Cannot create plot: {reason}")
            
            # Store the result for later export
            if result is not None and f_str is not None and method is not None:
                self.last_solution = (f_str, method, result, table_data)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error solving problem: {str(e)}")
            
            # Display error in table and result label
            if hasattr(self, 'result_table'):
                self.result_table.display(f"Error: {str(e)}")
            
            if hasattr(self, 'result_label'):
                self.result_label.configure(text=f"Error: {str(e)}")
            
            # Show error in plot area
            self._show_plot_error(f"Error: {str(e)}")
            
            return None
    
    def _show_plot_error(self, message="Error generating plot"):
        """Show an error message in the plot frame."""
        try:
            # Clear the plot frame
            if hasattr(self, 'plot_frame'):
                for widget in self.plot_frame.winfo_children():
                    try:
                        widget.destroy()
                    except Exception:
                        pass
                
                # Add an error label
                error_label = ctk.CTkLabel(
                    self.plot_frame,
                    text=message,
                    font=ctk.CTkFont(size=14),
                    text_color="red"
                )
                error_label.pack(pady=20)
        except Exception as e:
            self.logger.error(f"Error showing plot error: {str(e)}")

    def export_solution(self):
        if hasattr(self, "last_solution"):
            try:
                func, method, root, table_data = self.last_solution
                from datetime import datetime
                filename = f"solution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                export_to_pdf(filename, func, method, root, table_data)
                self.result_label.configure(text=f"Exported to {filename}")
            except Exception as e:
                self.logger.error(f"Error exporting solution: {str(e)}")
                self.result_label.configure(text=f"Export error: {str(e)}")

    def clear_content(self):
        """Clear all widgets from the content frame."""
        try:
            if hasattr(self, "content_frame") and self.content_frame.winfo_exists():
                # Destroy all widgets in the content frame
                for widget in self.content_frame.winfo_children():
                    if widget.winfo_exists():
                        widget.destroy()
                        
                # Reset references to content-specific widgets
                if hasattr(self, "input_form"):
                    delattr(self, "input_form")
                if hasattr(self, "result_table"):
                    delattr(self, "result_table")
                if hasattr(self, "result_label"):
                    delattr(self, "result_label")
                if hasattr(self, "history_table"):
                    delattr(self, "history_table")
                    
        except Exception as e:
            self.logger.error(f"Error clearing content: {str(e)}")
            # Continue execution even if there's an error

    def show_history(self):
        """Display the history screen."""
        try:
            self.clear_content()
            
            # Create a frame for the history table that takes up most of the space
            history_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            history_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create a label for the history
            history_label = ctk.CTkLabel(
                history_frame,
                text="Calculation History",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=self.theme.get("text", "#1E293B")
            )
            history_label.pack(pady=(0, 10))
            
            # Create a container frame for the table with fixed height
            table_container = ctk.CTkFrame(history_frame, fg_color=self.theme.get("bg", "#F0F4F8"), height=400)
            table_container.pack(fill="both", expand=True, padx=5, pady=5)
            table_container.pack_propagate(False)  # Prevent the frame from resizing based on its children
            
            # Create the history table with fixed height
            self.history_table = ResultTable(table_container, self.theme, height=400, fixed_position=True)
            self.history_table.table_frame.pack(fill="both", expand=True)
            
            # Load and display history data
            try:
                history_data = self.history_manager.load_history()
                self.history_table.display_history(history_data)
                
                # Display last solution if available
                if hasattr(self, "last_solution") and self.last_solution:
                    try:
                        func, method, root, table_data = self.last_solution
                        
                        # Create a frame for the last solution
                        last_solution_frame = ctk.CTkFrame(history_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
                        last_solution_frame.pack(fill="x", padx=5, pady=10)
                        
                        # Add a label for the last solution
                        last_solution_label = ctk.CTkLabel(
                            last_solution_frame,
                            text="Last Solution",
                            font=ctk.CTkFont(size=18, weight="bold"),
                            text_color=self.theme.get("text", "#1E293B")
                        )
                        last_solution_label.pack(pady=(0, 5))
                        
                        # Create a frame for the solution details
                        details_frame = ctk.CTkFrame(last_solution_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
                        details_frame.pack(fill="x", padx=10, pady=5)
                        
                        # Display function and method
                        ctk.CTkLabel(
                            details_frame,
                            text=f"Function: {func}",
                            font=ctk.CTkFont(size=14),
                            text_color=self.theme.get("text", "#1E293B")
                        ).pack(anchor="w", pady=2)
                        
                        ctk.CTkLabel(
                            details_frame,
                            text=f"Method: {method}",
                            font=ctk.CTkFont(size=14),
                            text_color=self.theme.get("text", "#1E293B")
                        ).pack(anchor="w", pady=2)
                        
                        # Display root if available
                        if root is not None:
                            ctk.CTkLabel(
                                details_frame,
                                text=f"Root: {root}",
                                font=ctk.CTkFont(size=14, weight="bold"),
                                text_color=self.theme.get("accent", "#0EA5E9")
                            ).pack(anchor="w", pady=2)
                        
                        # Add a button to view the full solution
                        def view_full_solution():
                            # Create a new window for the full solution
                            solution_window = ctk.CTkToplevel(self.root)
                            solution_window.title("Full Solution")
                            solution_window.geometry("800x600")
                            solution_window.grab_set()  # Make the window modal
                            
                            # Create a frame for the solution
                            solution_frame = ctk.CTkFrame(solution_window, fg_color=self.theme.get("bg", "#F0F4F8"))
                            solution_frame.pack(fill="both", expand=True, padx=10, pady=10)
                            
                            # Add a label for the solution
                            ctk.CTkLabel(
                                solution_frame,
                                text="Full Solution Details",
                                font=ctk.CTkFont(size=20, weight="bold"),
                                text_color=self.theme.get("text", "#1E293B")
                            ).pack(pady=(0, 10))
                            
                            # Create a container for the solution table with fixed height
                            solution_table_container = ctk.CTkFrame(solution_frame, fg_color=self.theme.get("bg", "#F0F4F8"), height=400)
                            solution_table_container.pack(fill="both", expand=True, padx=5, pady=5)
                            solution_table_container.pack_propagate(False)  # Prevent container from resizing
                            
                            # Create the table with fixed position
                            solution_table = ResultTable(solution_table_container, self.theme, height=400, fixed_position=True)
                            solution_table.table_frame.pack(fill="both", expand=True)
                            solution_table.display(table_data)
                            
                            # Add a close button
                            ctk.CTkButton(
                                solution_frame,
                                text="Close",
                                command=solution_window.destroy,
                                fg_color=self.theme.get("primary", "#3B82F6"),
                                hover_color=self.theme.get("primary_hover", "#2563EB"),
                                text_color="white",
                                font=ctk.CTkFont(size=14, weight="bold")
                            ).pack(pady=10)
                        
                        view_button = ctk.CTkButton(
                            details_frame,
                            text="View Full Solution",
                            command=view_full_solution,
                            fg_color=self.theme.get("primary", "#3B82F6"),
                            hover_color=self.theme.get("primary_hover", "#2563EB"),
                            text_color="white",
                            font=ctk.CTkFont(size=14, weight="bold")
                        )
                        view_button.pack(pady=10)
                        
                    except Exception as solution_error:
                        self.logger.error(f"Error displaying last solution: {str(solution_error)}")
            except Exception as history_error:
                self.logger.error(f"Error loading history data: {str(history_error)}")
                self.history_table.display({"Error": f"Error loading history: {str(history_error)}"})
            
            # Create button container
            button_container = ctk.CTkFrame(history_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            button_container.pack(fill="x", pady=10)
            
            # Add a back button at the bottom
            back_button = ctk.CTkButton(
                button_container,
                text="Back to Home",
                command=self.show_home,
                fg_color=self.theme.get("primary", "#3B82F6"),
                hover_color=self.theme.get("primary_hover", "#2563EB"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            back_button.pack(side="right", padx=10, expand=True)
            
            # Add a clear history button
            def clear_history():
                try:
                    if self.history_manager.clear_history():
                        # Reload the history data
                        history_data = self.history_manager.load_history()
                        self.history_table.display_history(history_data)
                        
                        # Show success message
                        success_label = ctk.CTkLabel(
                            history_frame, 
                            text="History cleared successfully!", 
                            text_color="green", 
                            font=ctk.CTkFont(size=14)
                        )
                        success_label.pack(pady=10)
                        
                        # Remove the success message after 3 seconds
                        self.root.after(3000, success_label.destroy)
                    else:
                        raise Exception("Failed to clear history")
                except Exception as e:
                    self.logger.error(f"Error clearing history: {str(e)}")
                    error_label = ctk.CTkLabel(
                        history_frame, 
                        text=f"Error clearing history: {str(e)}", 
                        text_color="red", 
                        font=ctk.CTkFont(size=14)
                    )
                    error_label.pack(pady=10)
                    
                    # Remove the error message after 5 seconds
                    self.root.after(5000, error_label.destroy)
            
            clear_button = ctk.CTkButton(
                button_container,
                text="Clear History",
                command=clear_history,
                fg_color=self.theme.get("secondary", "#64748B"),
                hover_color=self.theme.get("secondary_hover", "#475569"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            clear_button.pack(side="left", padx=10, expand=True)
            
        except Exception as e:
            self.logger.error(f"Error showing history screen: {str(e)}")
            # Create a basic error display if the history frame creation fails
            error_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            error_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"Error loading history screen: {str(e)}",
                text_color="red",
                font=ctk.CTkFont(size=14)
            )
            error_label.pack(pady=10)
            
            # Add a back button to return to home
            back_button = ctk.CTkButton(
                error_frame,
                text="Back to Home",
                command=self.show_home,
                fg_color=self.theme.get("primary", "#3B82F6"),
                hover_color=self.theme.get("primary_hover", "#2563EB"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            back_button.pack(pady=10)

    def show_settings(self):
        """Display the settings screen with error handling."""
        try:
            self.clear_content()
            
            # Create a frame for the settings
            settings_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Add a title
            title_label = ctk.CTkLabel(
                settings_frame, 
                text="Settings", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=self.theme.get("text", "#1E293B")
            )
            title_label.pack(pady=(20, 30))
            
            # Create a scrollable frame for settings
            scrollable_frame = ctk.CTkScrollableFrame(
                settings_frame, 
                fg_color=self.theme.get("bg", "#F0F4F8"),
                width=600,
                height=400
            )
            scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Default Decimal Places
            decimal_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            decimal_frame.pack(fill="x", pady=10)
            
            decimal_label = ctk.CTkLabel(
                decimal_frame, 
                text="Default Decimal Places:", 
                font=ctk.CTkFont(size=16),
                text_color=self.theme.get("text", "#1E293B")
            )
            decimal_label.pack(side="left", padx=10)
            
            decimal_var = ctk.StringVar(value=str(self.solver.decimal_places))
            decimal_entry = ctk.CTkEntry(
                decimal_frame, 
                width=100, 
                textvariable=decimal_var,
                placeholder_text="e.g., 6"
            )
            decimal_entry.pack(side="left", padx=10)
            
            # Maximum Iterations
            iter_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            iter_frame.pack(fill="x", pady=10)
            
            iter_label = ctk.CTkLabel(
                iter_frame, 
                text="Maximum Iterations:", 
                font=ctk.CTkFont(size=16),
                text_color=self.theme.get("text", "#1E293B")
            )
            iter_label.pack(side="left", padx=10)
            
            iter_var = ctk.StringVar(value=str(self.solver.max_iter))
            iter_entry = ctk.CTkEntry(
                iter_frame, 
                width=100, 
                textvariable=iter_var,
                placeholder_text="e.g., 50"
            )
            iter_entry.pack(side="left", padx=10)
            
            # Error Tolerance
            eps_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            eps_frame.pack(fill="x", pady=10)
            
            eps_label = ctk.CTkLabel(
                eps_frame, 
                text="Error Tolerance:", 
                font=ctk.CTkFont(size=16),
                text_color=self.theme.get("text", "#1E293B")
            )
            eps_label.pack(side="left", padx=10)
            
            eps_var = ctk.StringVar(value=str(self.solver.eps))
            eps_entry = ctk.CTkEntry(
                eps_frame, 
                width=100, 
                textvariable=eps_var,
                placeholder_text="e.g., 0.0001"
            )
            eps_entry.pack(side="left", padx=10)
            
            # Maximum Epsilon Value
            max_eps_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            max_eps_frame.pack(fill="x", pady=10)
            
            max_eps_label = ctk.CTkLabel(
                max_eps_frame, 
                text="Maximum Epsilon Value:", 
                font=ctk.CTkFont(size=16),
                text_color=self.theme.get("text", "#1E293B")
            )
            max_eps_label.pack(side="left", padx=10)
            
            max_eps_var = ctk.StringVar(value=str(getattr(self.solver, "max_eps", 1.0)))
            max_eps_entry = ctk.CTkEntry(
                max_eps_frame, 
                width=100, 
                textvariable=max_eps_var,
                placeholder_text="e.g., 1.0"
            )
            max_eps_entry.pack(side="left", padx=10)
            
            # Stop Condition
            stop_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            stop_frame.pack(fill="x", pady=10)
            
            stop_label = ctk.CTkLabel(
                stop_frame, 
                text="Stop Condition:", 
                font=ctk.CTkFont(size=16),
                text_color=self.theme.get("text", "#1E293B")
            )
            stop_label.pack(side="left", padx=10)
            
            stop_var = ctk.StringVar(value="Error Tolerance" if self.solver.stop_by_eps else "Maximum Iterations")
            stop_option = ctk.CTkOptionMenu(
                stop_frame, 
                values=["Error Tolerance", "Maximum Iterations"], 
                variable=stop_var, 
                fg_color=self.theme.get("button", "#3B82F6"), 
                button_color=self.theme.get("button_hover", "#2563EB"),
                button_hover_color=self.theme.get("accent", "#0EA5E9")
            )
            stop_option.pack(side="left", padx=10)
            
            # Create button container
            button_container = ctk.CTkFrame(settings_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            button_container.pack(fill="x", pady=10)
            
            # Save Button
            def save_settings():
                try:
                    # Validate and save decimal places
                    try:
                        decimal_places = int(decimal_var.get())
                        if decimal_places < 0:
                            raise ValueError("Decimal places must be non-negative")
                        self.solver.decimal_places = decimal_places
                    except ValueError as e:
                        raise ValueError(f"Invalid decimal places: {str(e)}")
                    
                    # Validate and save maximum iterations
                    try:
                        max_iter = int(iter_var.get())
                        if max_iter <= 0:
                            raise ValueError("Maximum iterations must be positive")
                        self.solver.max_iter = max_iter
                    except ValueError as e:
                        raise ValueError(f"Invalid maximum iterations: {str(e)}")
                    
                    # Validate and save error tolerance
                    try:
                        eps = float(eps_var.get())
                        if eps <= 0:
                            raise ValueError("Error tolerance must be positive")
                        self.solver.eps = eps
                    except ValueError as e:
                        raise ValueError(f"Invalid error tolerance: {str(e)}")
                    
                    # Validate and save maximum epsilon value
                    try:
                        max_eps = float(max_eps_var.get())
                        if max_eps <= 0:
                            raise ValueError("Maximum epsilon value must be positive")
                        self.solver.max_eps = max_eps
                    except ValueError as e:
                        raise ValueError(f"Invalid maximum epsilon value: {str(e)}")
                    
                    # Save stop condition
                    self.solver.stop_by_eps = stop_var.get() == "Error Tolerance"
                    
                    # Show success message
                    success_label = ctk.CTkLabel(
                        settings_frame, 
                        text="Settings saved successfully!", 
                        text_color="green", 
                        font=ctk.CTkFont(size=14)
                    )
                    success_label.pack(pady=10)
                    
                    # Remove the success message after 3 seconds
                    self.root.after(3000, success_label.destroy)
                    
                except Exception as e:
                    self.logger.error(f"Error saving settings: {str(e)}")
                    error_label = ctk.CTkLabel(
                        settings_frame, 
                        text=f"Error saving settings: {str(e)}", 
                        text_color="red", 
                        font=ctk.CTkFont(size=14)
                    )
                    error_label.pack(pady=10)
                    
                    # Remove the error message after 5 seconds
                    self.root.after(5000, error_label.destroy)
            
            save_button = ctk.CTkButton(
                button_container, 
                text="Save Settings", 
                command=save_settings,
                fg_color=self.theme.get("primary", "#3B82F6"), 
                hover_color=self.theme.get("primary_hover", "#2563EB"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            save_button.pack(side="left", padx=10, expand=True)
            
            # Reset Button
            def reset_settings():
                try:
                    self.solver.decimal_places = 6
                    self.solver.max_iter = 50
                    self.solver.eps = 0.0001
                    self.solver.stop_by_eps = True
                    
                    decimal_var.set("6")
                    iter_var.set("50")
                    eps_var.set("0.0001")
                    stop_var.set("Error Tolerance")
                    
                    reset_label = ctk.CTkLabel(
                        settings_frame, 
                        text="Settings reset to defaults!", 
                        text_color="green", 
                        font=ctk.CTkFont(size=14)
                    )
                    reset_label.pack(pady=10)
                    
                    # Remove the reset message after 3 seconds
                    self.root.after(3000, reset_label.destroy)
                    
                except Exception as e:
                    self.logger.error(f"Error resetting settings: {str(e)}")
                    error_label = ctk.CTkLabel(
                        settings_frame, 
                        text=f"Error resetting settings: {str(e)}", 
                        text_color="red", 
                        font=ctk.CTkFont(size=14)
                    )
                    error_label.pack(pady=10)
                    
                    # Remove the error message after 5 seconds
                    self.root.after(5000, error_label.destroy)
            
            reset_button = ctk.CTkButton(
                button_container, 
                text="Reset to Defaults", 
                command=reset_settings,
                fg_color=self.theme.get("secondary", "#64748B"), 
                hover_color=self.theme.get("secondary_hover", "#475569"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            reset_button.pack(side="right", padx=10, expand=True)
            
            # Add a back button
            back_button = ctk.CTkButton(
                button_container,
                text="Back to Home",
                command=self.show_home,
                fg_color=self.theme.get("primary", "#3B82F6"),
                hover_color=self.theme.get("primary_hover", "#2563EB"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            back_button.pack(side="right", padx=10, expand=True)
            
        except Exception as e:
            self.logger.error(f"Error showing settings: {str(e)}")
            # Create a basic error display if the settings frame creation fails
            error_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            error_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            error_label = ctk.CTkLabel(
                error_frame, 
                text=f"Error loading settings: {str(e)}", 
                text_color="red", 
                font=ctk.CTkFont(size=14)
            )
            error_label.pack(pady=10)
            
            # Add a back button to return to home
            back_button = ctk.CTkButton(
                error_frame,
                text="Back to Home",
                command=self.show_home,
                fg_color=self.theme.get("primary", "#3B82F6"),
                hover_color=self.theme.get("primary_hover", "#2563EB"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            back_button.pack(pady=10)

    def show_about(self):
        """Display the about screen with application information."""
        try:
            self.clear_content()
            
            # Create a frame for the about screen
            about_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            about_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create a scrollable frame for content
            scrollable_frame = ctk.CTkScrollableFrame(about_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Application Title
            title_label = ctk.CTkLabel(
                scrollable_frame,
                text="Numerical Analysis Application",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=self.theme.get("text", "#1E293B")
            )
            title_label.pack(pady=(0, 10))
            
            # Version - safely handle if version is not defined
            version = getattr(self, "version", "1.0.0")
            version_label = ctk.CTkLabel(
                scrollable_frame,
                text=f"Version: {version}",
                font=ctk.CTkFont(size=16),
                text_color=self.theme.get("text", "#1E293B")
            )
            version_label.pack(pady=(0, 20))
            
            # Description
            description_text = """
            This application provides a comprehensive suite of numerical analysis tools for solving various mathematical problems.
            
            Features:
            • Multiple numerical methods for root finding
            • Interactive function plotting
            • Detailed solution steps and iterations
            • Export capabilities for results
            • Customizable settings
            
            The application is designed to help students and professionals understand and implement numerical methods effectively.
            """
            
            description_label = ctk.CTkLabel(
                scrollable_frame,
                text=description_text,
                font=ctk.CTkFont(size=14),
                text_color=self.theme.get("text", "#1E293B"),
                justify="left"
            )
            description_label.pack(pady=(0, 20), padx=20)
            
            # Credits
            credits_label = ctk.CTkLabel(
                scrollable_frame,
                text="Developed by Hosam Dyab + Hazem Mohamed using Python and CustomTkinter",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.theme.get("accent", "#0EA5E9")
            )
            credits_label.pack(pady=(0, 10))
            
            # Create button container
            button_container = ctk.CTkFrame(about_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            button_container.pack(fill="x", pady=10)
            
            # Back Button
            back_button = ctk.CTkButton(
                button_container,
                text="Back to Home",
                command=self.show_home,
                fg_color=self.theme.get("primary", "#3B82F6"),
                hover_color=self.theme.get("primary_hover", "#2563EB"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            back_button.pack(padx=10, expand=True)
            
        except Exception as e:
            self.logger.error(f"Error showing about screen: {str(e)}")
            # Create a basic error display if the about frame creation fails
            error_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme.get("bg", "#F0F4F8"))
            error_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"Error loading about screen: {str(e)}",
                text_color="red",
                font=ctk.CTkFont(size=14)
            )
            error_label.pack(pady=10)
            
            # Add a back button to return to home
            back_button = ctk.CTkButton(
                error_frame,
                text="Back to Home",
                command=self.show_home,
                fg_color=self.theme.get("primary", "#3B82F6"),
                hover_color=self.theme.get("primary_hover", "#2563EB"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            back_button.pack(pady=10)

    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error running application: {str(e)}")
            raise