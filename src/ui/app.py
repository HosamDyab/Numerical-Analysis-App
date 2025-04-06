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
        self.root = ctk.CTk()
        self.root.title("Numerical Analysis App")
        self.root.geometry("1000x700")
        self.logger = logging.getLogger(__name__)
        
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
            style.configure("Custom.Treeview",
                          background=self.theme["table_bg"],
                          foreground=self.theme["table_fg"],
                          fieldbackground=self.theme["table_bg"],
                          rowheight=25)
            style.configure("Custom.Treeview.Heading",
                          background=self.theme["table_heading_bg"],
                          foreground=self.theme["table_heading_fg"],
                          font=("Helvetica", 10, "bold"))
            style.map("Custom.Treeview",
                     background=[("selected", self.theme["button"])],
                     foreground=[("selected", self.theme["text"])])
        except Exception as e:
            self.logger.error(f"Error configuring table style: {str(e)}")

    def setup_welcome_screen(self):
        self.welcome_frame = ctk.CTkFrame(self.root, fg_color=self.theme["bg"])
        self.welcome_frame.pack(fill="both", expand=True)
        label = ctk.CTkLabel(self.welcome_frame, text="Numerical Analysis App", font=("Helvetica", 48, "bold"), text_color=self.theme["accent"])
        label.pack(expand=True)
        self.root.after(2000, self.show_main_window)

    def show_main_window(self):
        self.welcome_frame.destroy()
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.theme["bg"])
        self.main_frame.pack(fill="both", expand=True)

        self.header = ctk.CTkFrame(self.main_frame, height=60, fg_color=self.theme["fg"])
        self.header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.header, text="Numerical Analysis", font=("Helvetica", 24, "bold"), text_color=self.theme["accent"]).pack(side="left", padx=20)
        theme_menu = ctk.CTkOptionMenu(self.header, values=list(self.theme_manager.themes.keys()), 
                                      command=self.change_theme, fg_color=self.theme["button"], 
                                      button_color=self.theme["button_hover"], button_hover_color=self.theme["accent"])
        theme_menu.pack(side="right", padx=20)

        self.sidebar = Sidebar(self.main_frame, self.theme, self.show_home, self.show_history, 
                              self.show_settings, self.show_about)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=self.theme["bg"])
        self.content_frame.pack(side="left", fill="both", expand=True)
        self.show_home()

    def change_theme(self, theme_name: str):
        self.theme = self.theme_manager.set_theme(theme_name)
        self.update_ui_theme()

    def update_ui_theme(self):
        try:
            self.main_frame.configure(fg_color=self.theme["bg"])
            self.header.configure(fg_color=self.theme["fg"])
            self.content_frame.configure(fg_color=self.theme["bg"])
            self.sidebar.update_theme(self.theme)
            
            # Update table style
            style = ttk.Style()
            style.configure("Custom.Treeview",
                          background=self.theme["table_bg"],
                          foreground=self.theme["table_fg"],
                          fieldbackground=self.theme["table_bg"])
            style.configure("Custom.Treeview.Heading",
                          background=self.theme["table_heading_bg"],
                          foreground=self.theme["table_heading_fg"])
            
            if hasattr(self, "home_frame"):
                self.input_form.update_theme(self.theme)
                self.result_table.table.configure(style="Custom.Treeview")
                self.result_label.configure(text_color=self.theme["text"])
            elif hasattr(self, "history_frame"):
                self.history_frame.configure(fg_color=self.theme["bg"])
                for w in self.history_frame.winfo_children():
                    if isinstance(w, (ctk.CTkButton, ctk.CTkLabel)):
                        w.configure(text_color=self.theme["text"], fg_color=self.theme["button"], hover_color=self.theme["button_hover"])
        except Exception as e:
            self.logger.error(f"Error updating UI theme: {str(e)}")

    def show_home(self):
        try:
            self.clear_content()
            self.home_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme["bg"])
            self.home_frame.pack(fill="both", expand=True, padx=20, pady=20)

            self.input_form = InputForm(self.home_frame, self.theme, list(self.solver.methods.keys()), self.solve)
            self.input_form.frame.pack(side="top", fill="x", pady=(0, 20))
            
            # Create a frame for the table to ensure proper sizing
            table_container = ctk.CTkFrame(self.home_frame, fg_color=self.theme["bg"])
            table_container.pack(side="top", fill="both", expand=True, pady=(0, 20))
            
            self.result_table = ResultTable(table_container)
            self.result_table.table_frame.pack(fill="both", expand=True)
            
            self.result_label = ctk.CTkLabel(self.home_frame, text="", text_color=self.theme["text"], font=("Helvetica", 14))
            self.result_label.pack(pady=10)
            
            ctk.CTkButton(self.home_frame, text="Export to PDF", command=self.export_solution, 
                         fg_color=self.theme["button"], hover_color=self.theme["button_hover"], font=("Helvetica", 12)).pack(pady=10)
        except Exception as e:
            self.logger.error(f"Error showing home screen: {str(e)}")

    def solve(self, func: str, method: str, params: dict, eps: float, max_iter: int, stop_by_eps: bool, decimal_places: int = 6):
        try:
            if not func:
                self.result_label.configure(text="Error: No function provided")
                return

            root, table_data = self.solver.solve(method, func, params, eps, max_iter, stop_by_eps, decimal_places)
            self.last_solution = (func, method, root, table_data)
            
            # Update the table with results
            self.result_table.display(table_data)
            
            if isinstance(table_data, dict) and "Error" in table_data:
                self.result_label.configure(text=table_data["Error"])
            elif root is not None:
                self.result_label.configure(text=f"The Required Root is: {root:.{decimal_places}f}")
                self.history_manager.save_solution(func, method, root, table_data)
            else:
                self.result_label.configure(text="No root found")
        except Exception as e:
            self.logger.error(f"Error in solve method: {str(e)}")
            self.result_label.configure(text=f"Error: {str(e)}")

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
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_history(self):
        try:
            self.clear_content()
            self.history_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme["bg"])
            self.history_frame.pack(fill="both", expand=True, padx=20, pady=20)

            title = ctk.CTkLabel(self.history_frame, text="Calculation History", font=("Helvetica", 24, "bold"), text_color=self.theme["accent"])
            title.pack(pady=(0, 20))

            # Create a frame for the table to ensure proper sizing
            table_container = ctk.CTkFrame(self.history_frame, fg_color=self.theme["bg"])
            table_container.pack(fill="both", expand=True, pady=(0, 20))
            
            table = ResultTable(table_container)
            table.table_frame.pack(fill="both", expand=True)
            
            history = self.history_manager.load_history()
            table.display_history(history)

            button_frame = ctk.CTkFrame(self.history_frame, fg_color=self.theme["bg"])
            button_frame.pack(fill="x", pady=10)

            ctk.CTkButton(button_frame, text="Clear History", command=self.clear_history_and_update,
                         fg_color=self.theme["button"], hover_color=self.theme["button_hover"], 
                         font=("Helvetica", 14), width=150).pack(side="left", padx=10)
            if history:
                ctk.CTkButton(button_frame, text="View Last Solution", command=lambda: self.view_history(history[-1]),
                             fg_color=self.theme["button"], hover_color=self.theme["button_hover"], 
                             font=("Helvetica", 14), width=150).pack(side="left", padx=10)
        except Exception as e:
            self.logger.error(f"Error showing history: {str(e)}")

    def clear_history_and_update(self):
        self.history_manager.clear_history()
        self.show_history()

    def view_history(self, entry):
        try:
            self.show_home()
            self.input_form.func_entry.delete(0, "end")
            self.input_form.func_entry.insert(0, entry["function"])
            self.input_form.method_var.set(entry["method"])
            self.result_table.display(entry["table"])
            self.result_label.configure(text=f"The Required Root is: {entry['root']}")
            self.last_solution = (entry["function"], entry["method"], entry["root"], entry["table"])
        except Exception as e:
            self.logger.error(f"Error viewing history entry: {str(e)}")
            self.result_label.configure(text=f"Error loading history entry: {str(e)}")

    def show_settings(self):
        try:
            self.clear_content()
            settings_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme["bg"])
            settings_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Title
            title = ctk.CTkLabel(settings_frame, text="Settings", font=("Helvetica", 24, "bold"), text_color=self.theme["accent"])
            title.pack(pady=(0, 20))

            # Create a scrollable frame for settings
            scrollable_frame = ctk.CTkScrollableFrame(settings_frame, fg_color=self.theme["bg"])
            scrollable_frame.pack(fill="both", expand=True)

            # Default Decimal Places
            decimal_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.theme["bg"])
            decimal_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(decimal_frame, text="Default Decimal Places:", font=("Helvetica", 14), text_color=self.theme["text"]).pack(side="left", padx=10)
            decimal_var = ctk.StringVar(value=str(self.solver.decimal_places))
            decimal_entry = ctk.CTkEntry(decimal_frame, textvariable=decimal_var, width=50)
            decimal_entry.pack(side="left", padx=10)

            # Default Maximum Iterations
            iter_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.theme["bg"])
            iter_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(iter_frame, text="Default Maximum Iterations:", font=("Helvetica", 14), text_color=self.theme["text"]).pack(side="left", padx=10)
            iter_var = ctk.StringVar(value=str(self.solver.max_iter))
            iter_entry = ctk.CTkEntry(iter_frame, textvariable=iter_var, width=50)
            iter_entry.pack(side="left", padx=10)

            # Default Error Tolerance
            eps_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.theme["bg"])
            eps_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(eps_frame, text="Default Error Tolerance:", font=("Helvetica", 14), text_color=self.theme["text"]).pack(side="left", padx=10)
            eps_var = ctk.StringVar(value=str(self.solver.eps))
            eps_entry = ctk.CTkEntry(eps_frame, textvariable=eps_var, width=50)
            eps_entry.pack(side="left", padx=10)

            # Default Stop Condition
            stop_frame = ctk.CTkFrame(scrollable_frame, fg_color=self.theme["bg"])
            stop_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(stop_frame, text="Default Stop Condition:", font=("Helvetica", 14), text_color=self.theme["text"]).pack(side="left", padx=10)
            stop_var = ctk.StringVar(value="Error Tolerance" if self.solver.stop_by_eps else "Maximum Iterations")
            stop_option = ctk.CTkOptionMenu(stop_frame, values=["Error Tolerance", "Maximum Iterations"], 
                                          variable=stop_var, fg_color=self.theme["button"], 
                                          button_color=self.theme["button_hover"])
            stop_option.pack(side="left", padx=10)

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

                    # Save stop condition
                    self.solver.stop_by_eps = stop_var.get() == "Error Tolerance"

                    # Show success message
                    ctk.CTkLabel(settings_frame, text="Settings saved successfully!", 
                                text_color="green", font=("Helvetica", 12)).pack(pady=10)
                except Exception as e:
                    ctk.CTkLabel(settings_frame, text=f"Error saving settings: {str(e)}", 
                                text_color="red", font=("Helvetica", 12)).pack(pady=10)

            save_button = ctk.CTkButton(settings_frame, text="Save Settings", command=save_settings,
                                      fg_color=self.theme["button"], hover_color=self.theme["button_hover"],
                                      font=("Helvetica", 14))
            save_button.pack(pady=20)

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
                    
                    ctk.CTkLabel(settings_frame, text="Settings reset to defaults!", 
                                text_color="green", font=("Helvetica", 12)).pack(pady=10)
                except Exception as e:
                    ctk.CTkLabel(settings_frame, text=f"Error resetting settings: {str(e)}", 
                                text_color="red", font=("Helvetica", 12)).pack(pady=10)

            reset_button = ctk.CTkButton(settings_frame, text="Reset to Defaults", command=reset_settings,
                                       fg_color=self.theme["button"], hover_color=self.theme["button_hover"],
                                       font=("Helvetica", 14))
            reset_button.pack(pady=10)

        except Exception as e:
            self.logger.error(f"Error showing settings: {str(e)}")
            ctk.CTkLabel(settings_frame, text=f"Error loading settings: {str(e)}", 
                        text_color="red", font=("Helvetica", 12)).pack(pady=10)

    def show_about(self):
        self.clear_content()
        about_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme["bg"])
        about_frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(about_frame, text="Numerical Analysis App\nDeveloped by Hosam Dyab \nVersion 1.0",
                    text_color=self.theme["text"], font=("Helvetica", 20)).pack(pady=20)

    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error running application: {str(e)}")
            raise