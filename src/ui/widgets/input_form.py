import customtkinter as ctk
from tkinter import messagebox
import logging
import math

class InputForm:
    def __init__(self, parent, theme: dict, methods: list, solve_callback):
        self.parent = parent
        self.theme = theme
        self.solve_callback = solve_callback
        self.method_var = ctk.StringVar(value="Bisection")
        self.frame = ctk.CTkFrame(parent, fg_color=theme["bg"])
        self.logger = logging.getLogger(__name__)
        self.MAX_EPS = 100.0  # Increased maximum allowed epsilon value to 100
        
        # Method-specific example functions dictionary
        self.example_functions = {
            "Bisection": {
                "Select Example": "",
                "4*x**3 - 6*x**2 + 7*x - 2.3": "4*x**3 - 6*x**2 + 7*x - 2.3",
                "x**2 - 4": "x**2 - 4",
                "x**3 - 2*x + 1": "x**3 - 2*x + 1",
                "sin(x)": "sin(x)",
                "cos(x)": "cos(x)",
                "x**4 - 3*x**2 + 2": "x**4 - 3*x**2 + 2",
                "exp(x) - 2": "exp(x) - 2",
                "log(x) - 1": "log(x) - 1",
                "x**5 - 5*x + 3": "x**5 - 5*x + 3",
                "tan(x) - x": "tan(x) - x"
            },
            "False Position": {
                "Select Example": "",
                "x * log(x) - 1.2": "x * log(x) - 1.2",
                "x**2 - 4": "x**2 - 4",
                "x**3 - 2*x + 1": "x**3 - 2*x + 1",
                "sin(x)": "sin(x)",
                "cos(x)": "cos(x)",
                "x**4 - 10*x**2 + 9": "x**4 - 10*x**2 + 9",
                "exp(x) - 3*x": "exp(x) - 3*x",
                "log(x) + x - 2": "log(x) + x - 2",
                "x**3 + 4*x**2 - 10": "x**3 + 4*x**2 - 10",
                "tan(x) - 2*x": "tan(x) - 2*x"
            },
            "Fixed Point": {
                "Select Example": "",
                "sin(sqrt(x))": "sin(sqrt(x))",
                "x**2 - 4": "x**2 - 4",
                "x**3 - 2*x + 1": "x**3 - 2*x + 1",
                "sin(x)": "sin(x)",
                "cos(x)": "cos(x)",
                "sqrt(2 - x)": "sqrt(2 - x)",
                "exp(-x)": "exp(-x)",
                "1/x": "1/x",
                "x**2/3": "x**2/3",
                "cos(x)/2": "cos(x)/2"
            },
            "Newton-Raphson": {
                "Select Example": "",
                "2 + 6*x - 4*x**2 + 0.5*x**3": "2 + 6*x - 4*x**2 + 0.5*x**3",
                "x**2 - 4": "x**2 - 4",
                "x**3 - 2*x + 1": "x**3 - 2*x + 1",
                "sin(x)": "sin(x)",
                "cos(x)": "cos(x)",
                "x**4 - 16": "x**4 - 16",
                "exp(x) - 5": "exp(x) - 5",
                "log(x) - 1": "log(x) - 1",
                "x**5 - 32": "x**5 - 32",
                "tan(x) - 1": "tan(x) - 1",
                "exp(-x) - sin(x)": "exp(-x) - sin(x)",
                "e^-x - sin(x)": "e^-x - sin(x)",
                "2*sin(sqrt(x)) - x": "2*sin(sqrt(x)) - x",
                "x**3 + x**2 - 3*x - 3": "x**3 + x**2 - 3*x - 3",
                "x**2 - 2*x - 1": "x**2 - 2*x - 1",
                "x**3 - 3*x + 1": "x**3 - 3*x + 1",
                "x**4 - 3*x**2 + 2": "x**4 - 3*x**2 + 2",
                "x**5 - 5*x + 3": "x**5 - 5*x + 3",
                "x**6 - 6*x + 4": "x**6 - 6*x + 4",
                "x**7 - 7*x + 5": "x**7 - 7*x + 5",
                "x**8 - 8*x + 6": "x**8 - 8*x + 6",
                "x**9 - 9*x + 7": "x**9 - 9*x + 7",
                "x**10 - 10*x + 8": "x**10 - 10*x + 8"
            },
            "Secant": {
                "Select Example": "",
                "-x**3 + 7.89*x + 11": "-x**3 + 7.89*x + 11",
                "x**2 - 4": "x**2 - 4",
                "x**3 - 2*x + 1": "x**3 - 2*x + 1",
                "sin(x)": "sin(x)",
                "cos(x)": "cos(x)",
                "x**4 - 81": "x**4 - 81",
                "exp(x) - 10": "exp(x) - 10",
                "log(x) - 2": "log(x) - 2",
                "x**5 - 243": "x**5 - 243",
                "tan(x) - 3": "tan(x) - 3"
            }
        }
        
        # Default example functions (used when method changes)
        self.default_examples = list(self.example_functions["Bisection"].keys())
        
        self.setup_widgets(methods)

    def setup_widgets(self, methods):
        # Function input row with example dropdown
        func_frame = ctk.CTkFrame(self.frame, fg_color=self.theme["bg"])
        func_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")
        
        ctk.CTkLabel(func_frame, text="Function f(x):", text_color=self.theme["text"], 
                    font=("Helvetica", 12, "bold")).pack(side="left", padx=10)
        self.func_entry = ctk.CTkEntry(func_frame, width=250, placeholder_text="Enter function (e.g., x**2 - 4)")
        self.func_entry.pack(side="left", padx=5)
        
        # Example functions dropdown
        self.example_var = ctk.StringVar(value="Select Example")
        self.example_menu = ctk.CTkOptionMenu(
            func_frame,
            values=self.default_examples,
            variable=self.example_var,
            command=self.load_example,
            fg_color=self.theme["button"],
            button_color=self.theme["button_hover"],
            button_hover_color=self.theme["accent"],
            width=200
        )
        self.example_menu.pack(side="left", padx=10)

        # Method selection
        method_frame = ctk.CTkFrame(self.frame, fg_color=self.theme["bg"])
        method_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        
        ctk.CTkLabel(method_frame, text="Method:", text_color=self.theme["text"], 
                    font=("Helvetica", 12, "bold")).pack(side="left", padx=10)
        self.method_menu = ctk.CTkOptionMenu(
            method_frame, 
            variable=self.method_var, 
            values=methods, 
            command=self.update_fields,
            fg_color=self.theme["button"], 
            button_color=self.theme["button_hover"],
            button_hover_color=self.theme["accent"],
            font=("Helvetica", 12, "bold")
        )
        self.method_menu.pack(side="left", padx=5)

        # Parameters frame
        self.input_frame = ctk.CTkFrame(self.frame, fg_color=self.theme["bg"])
        self.input_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.update_fields("Bisection")

        # Settings frame
        settings_frame = ctk.CTkFrame(self.frame, fg_color=self.theme["bg"])
        settings_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Epsilon and Max Iterations
        eps_frame = ctk.CTkFrame(settings_frame, fg_color=self.theme["bg"])
        eps_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")
        
        ctk.CTkLabel(eps_frame, text="Epsilon:", text_color=self.theme["text"]).pack(side="left", padx=10)
        self.eps_entry = ctk.CTkEntry(eps_frame, width=100, placeholder_text="0.0001")
        self.eps_entry.pack(side="left", padx=5)
        
        # Add comparison operator dropdown
        self.eps_operator = ctk.CTkOptionMenu(
            eps_frame,
            values=["<=", ">=", "<", ">", "="],
            width=60,
            fg_color=self.theme["button"],
            button_color=self.theme["button_hover"],
            button_hover_color=self.theme["accent"]
        )
        self.eps_operator.pack(side="left", padx=5)
        self.eps_operator.set("<=")  # Default operator
        
        ctk.CTkLabel(settings_frame, text="Max Iterations:", text_color=self.theme["text"]).grid(row=0, column=2, pady=5, padx=10, sticky="e")
        self.iter_entry = ctk.CTkEntry(settings_frame, width=150, placeholder_text="e.g., 50")
        self.iter_entry.grid(row=0, column=3, pady=5)
        
        # Round Result checkbox and decimal places
        self.round_var = ctk.BooleanVar(value=True)
        self.round_checkbox = ctk.CTkCheckBox(
            settings_frame, 
            text="Round Result", 
            variable=self.round_var,
            command=self.toggle_decimal_entry,
            text_color=self.theme["text"],
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"],
            checkmark_color="#FFFFFF"
        )
        self.round_checkbox.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="w")
        
        ctk.CTkLabel(settings_frame, text="Decimal Places:", text_color=self.theme["text"]).grid(row=1, column=2, pady=5, padx=10, sticky="e")
        self.decimal_entry = ctk.CTkEntry(settings_frame, width=150, placeholder_text="e.g., 6")
        self.decimal_entry.grid(row=1, column=3, pady=5)
        
        # Stop condition
        stop_frame = ctk.CTkFrame(self.frame, fg_color=self.theme["bg"])
        stop_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.stop_var = ctk.StringVar(value="Epsilon")
        ctk.CTkRadioButton(
            stop_frame, 
            text="Stop by Epsilon", 
            variable=self.stop_var, 
            value="Epsilon", 
            text_color=self.theme["text"],
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"]
        ).pack(side="left", padx=20)
        
        ctk.CTkRadioButton(
            stop_frame, 
            text="Stop by Iterations", 
            variable=self.stop_var, 
            value="Iterations", 
            text_color=self.theme["text"],
            fg_color=self.theme["button"],
            hover_color=self.theme["button_hover"]
        ).pack(side="left", padx=20)

        # Solve button
        ctk.CTkButton(
            self.frame, 
            text="Solve", 
            command=self.on_solve, 
            fg_color=self.theme["button"], 
            hover_color=self.theme["button_hover"], 
            font=("Helvetica", 14, "bold"),
            height=40
        ).grid(row=5, column=0, columnspan=2, pady=15)

    def toggle_decimal_entry(self):
        """Enable or disable the decimal places entry based on the round checkbox."""
        if self.round_var.get():
            self.decimal_entry.configure(state="normal")
        else:
            self.decimal_entry.configure(state="disabled")

    def load_example(self, example_name: str):
        """Load the selected example function into the input field."""
        method = self.method_var.get()
        if method in self.example_functions and example_name in self.example_functions[method]:
            self.func_entry.delete(0, "end")
            self.func_entry.insert(0, self.example_functions[method][example_name])

    def update_fields(self, method: str):
        """Update the input fields based on the selected method."""
        # Clear previous fields
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        # Update example functions dropdown
        if method in self.example_functions:
            self.example_menu.configure(values=list(self.example_functions[method].keys()))
            self.example_var.set("Select Example")
        
        # Create method-specific input fields
        self.entries = {}
        
        # Add a title for the parameters
        ctk.CTkLabel(
            self.input_frame, 
            text=f"{method} Parameters:", 
            text_color=self.theme["text"],
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
        
        if method in ["Bisection", "False Position"]:
            ctk.CTkLabel(self.input_frame, text="Lower Bound (Xl):", text_color=self.theme["text"]).grid(row=1, column=0, pady=5, padx=10, sticky="e")
            self.entries["xl"] = ctk.CTkEntry(self.input_frame, width=150, placeholder_text="e.g., 0")
            self.entries["xl"].grid(row=1, column=1, pady=5)
            
            ctk.CTkLabel(self.input_frame, text="Upper Bound (Xu):", text_color=self.theme["text"]).grid(row=2, column=0, pady=5, padx=10, sticky="e")
            self.entries["xu"] = ctk.CTkEntry(self.input_frame, width=150, placeholder_text="e.g., 2")
            self.entries["xu"].grid(row=2, column=1, pady=5)
            
        elif method in ["Fixed Point", "Newton-Raphson"]:
            ctk.CTkLabel(self.input_frame, text="Initial Value (X0):", text_color=self.theme["text"]).grid(row=1, column=0, pady=5, padx=10, sticky="e")
            self.entries["xi"] = ctk.CTkEntry(self.input_frame, width=150, placeholder_text="e.g., 1")
            self.entries["xi"].grid(row=1, column=1, pady=5)
            
        elif method == "Secant":
            ctk.CTkLabel(self.input_frame, text="First Initial Value (X-1):", text_color=self.theme["text"]).grid(row=1, column=0, pady=5, padx=10, sticky="e")
            self.entries["xi_minus_1"] = ctk.CTkEntry(self.input_frame, width=150, placeholder_text="e.g., 0")
            self.entries["xi_minus_1"].grid(row=1, column=1, pady=5)
            
            ctk.CTkLabel(self.input_frame, text="Second Initial Value (X0):", text_color=self.theme["text"]).grid(row=2, column=0, pady=5, padx=10, sticky="e")
            self.entries["xi"] = ctk.CTkEntry(self.input_frame, width=150, placeholder_text="e.g., 1")
            self.entries["xi"].grid(row=2, column=1, pady=5)

    def validate_input(self) -> tuple[bool, str]:
        """Validate all input fields and return (is_valid, error_message)."""
        try:
            # Validate function
            func = self.func_entry.get().strip()
            if not func:
                return False, "Function cannot be empty"
            
            # Try to parse the function with sympy (imported in solver.py)
            # This is just a basic check, actual parsing happens in the solver
            if "math." in func:
                # Replace math functions with their sympy equivalents
                func = func.replace("math.sin", "sp.sin").replace("math.cos", "sp.cos")
                func = func.replace("math.tan", "sp.tan").replace("math.exp", "sp.exp")
                func = func.replace("math.log", "sp.log").replace("math.sqrt", "sp.sqrt")
            
            # Validate epsilon
            try:
                eps = float(self.eps_entry.get() or "0.0001")
                if eps <= 0:
                    return False, "Epsilon must be positive"
                # Get epsilon operator
                eps_operator = self.eps_operator.get()
                # Check if epsilon satisfies the comparison
                if eps_operator == "<=" and eps > self.MAX_EPS:
                    return False, f"Epsilon must be less than or equal to {self.MAX_EPS}"
                elif eps_operator == ">=" and eps < self.MAX_EPS:
                    return False, f"Epsilon must be greater than or equal to {self.MAX_EPS}"
                elif eps_operator == "<" and eps >= self.MAX_EPS:
                    return False, f"Epsilon must be less than {self.MAX_EPS}"
                elif eps_operator == ">" and eps <= self.MAX_EPS:
                    return False, f"Epsilon must be greater than {self.MAX_EPS}"
                elif eps_operator == "=" and eps > self.MAX_EPS:
                    return False, f"Epsilon must be less than or equal to {self.MAX_EPS}"
            except ValueError:
                return False, "Epsilon must be a number"

            # Validate max iterations
            try:
                max_iter = int(self.iter_entry.get() or "50")
                if max_iter <= 0:
                    return False, "Maximum iterations must be positive"
            except ValueError:
                return False, "Maximum iterations must be an integer"

            # Validate decimal places if rounding is enabled
            if self.round_var.get():
                try:
                    decimal_places = int(self.decimal_entry.get() or "6")
                    if decimal_places < 0:
                        return False, "Decimal places must be non-negative"
                except ValueError:
                    return False, "Decimal places must be an integer"
            else:
                decimal_places = 10  # Use a high value for full precision

            # Validate method-specific parameters
            method = self.method_var.get()
            params = {}
            for key, entry in self.entries.items():
                try:
                    value = float(entry.get() or "0")
                    params[key] = value
                except ValueError:
                    return False, f"Invalid value for {key}"
                
            # Additional validation for Secant method
            if method == "Secant":
                if params.get("xi_minus_1") == params.get("xi"):
                    return False, "Initial values for Secant method must be different"
                
            # Additional validation for Bisection and False Position methods
            if method in ["Bisection", "False Position"]:
                if params.get("xl") >= params.get("xu"):
                    return False, "Lower bound must be less than upper bound"

            return True, ""
        except Exception as e:
            self.logger.error(f"Input validation error: {str(e)}")
            return False, f"Input validation error: {str(e)}"

    def on_solve(self):
        is_valid, error_msg = self.validate_input()
        if not is_valid:
            messagebox.showerror("Input Error", error_msg)
            return

        try:
            func = self.func_entry.get().strip()
            method = self.method_var.get()
            eps = float(self.eps_entry.get() or "0.0001")
            eps_operator = self.eps_operator.get()
            max_iter = int(self.iter_entry.get() or "50")
            decimal_places = int(self.decimal_entry.get() or "6") if self.round_var.get() else 10
            stop_by_eps = self.stop_var.get() == "Epsilon"
            params = {key: float(entry.get() or "0") for key, entry in self.entries.items()}
            self.solve_callback(func, method, params, eps, eps_operator, max_iter, stop_by_eps, decimal_places)
        except Exception as e:
            self.logger.error(f"Error in solve callback: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_theme(self, theme: dict):
        self.theme = theme
        self.frame.configure(fg_color=theme["bg"])
        self.input_frame.configure(fg_color=theme["bg"])
        
        # Update all widgets with enhanced styling
        for w in self.frame.winfo_children():
            if isinstance(w, ctk.CTkLabel):
                w.configure(text_color=theme["text"])
            elif isinstance(w, ctk.CTkButton):
                w.configure(
                    fg_color=theme["button"], 
                    hover_color=theme["button_hover"],
                    text_color="#FFFFFF"  # White text for better contrast
                )
            elif isinstance(w, ctk.CTkOptionMenu):
                w.configure(
                    fg_color=theme["button"], 
                    button_color=theme["button_hover"],
                    button_hover_color=theme["accent"],
                    text_color="#FFFFFF"  # White text for better contrast
                )
            elif isinstance(w, ctk.CTkRadioButton):
                w.configure(
                    text_color=theme["text"],
                    fg_color=theme["button"],
                    hover_color=theme["button_hover"],
                    text_color_disabled=theme["text"]  # Keep text visible even when disabled
                )
            elif isinstance(w, ctk.CTkEntry):
                w.configure(
                    border_color=theme["accent"],
                    text_color=theme["text"],
                    placeholder_text_color=theme["text"]  # Make placeholder text visible
                )
            elif isinstance(w, ctk.CTkFrame):
                w.configure(fg_color=theme["bg"])
            elif isinstance(w, ctk.CTkCheckBox):
                w.configure(
                    text_color=theme["text"],
                    fg_color=theme["button"],
                    hover_color=theme["button_hover"],
                    checkmark_color="#FFFFFF"
                )