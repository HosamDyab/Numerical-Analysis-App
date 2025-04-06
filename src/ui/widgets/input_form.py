import customtkinter as ctk
from tkinter import messagebox
import logging

class InputForm:
    def __init__(self, parent, theme: dict, methods: list, solve_callback):
        self.parent = parent
        self.theme = theme
        self.solve_callback = solve_callback
        self.method_var = ctk.StringVar(value="Bisection")
        self.frame = ctk.CTkFrame(parent, fg_color=theme["bg"])
        self.logger = logging.getLogger(__name__)
        self.setup_widgets(methods)

    def setup_widgets(self, methods):
        ctk.CTkLabel(self.frame, text="Function:", text_color=self.theme["text"]).grid(row=0, column=0, pady=5, padx=10, sticky="e")
        self.func_entry = ctk.CTkEntry(self.frame, width=250)
        self.func_entry.grid(row=0, column=1, pady=5)

        ctk.CTkLabel(self.frame, text="Method:", text_color=self.theme["text"]).grid(row=1, column=0, pady=5, padx=10, sticky="e")
        self.method_menu = ctk.CTkOptionMenu(self.frame, variable=self.method_var, values=methods, command=self.update_fields,
                                            fg_color=self.theme["button"], button_color=self.theme["button_hover"])
        self.method_menu.grid(row=1, column=1, pady=5)

        self.input_frame = ctk.CTkFrame(self.frame, fg_color=self.theme["bg"])
        self.input_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.update_fields("Bisection")

        ctk.CTkLabel(self.frame, text="Epsilon:", text_color=self.theme["text"]).grid(row=3, column=0, pady=5, padx=10, sticky="e")
        self.eps_entry = ctk.CTkEntry(self.frame, width=150)
        self.eps_entry.insert(0, "0.0001")
        self.eps_entry.grid(row=3, column=1, pady=5)

        ctk.CTkLabel(self.frame, text="Max Iter:", text_color=self.theme["text"]).grid(row=4, column=0, pady=5, padx=10, sticky="e")
        self.iter_entry = ctk.CTkEntry(self.frame, width=150)
        self.iter_entry.insert(0, "50")
        self.iter_entry.grid(row=4, column=1, pady=5)

        ctk.CTkLabel(self.frame, text="Decimals:", text_color=self.theme["text"]).grid(row=5, column=0, pady=5, padx=10, sticky="e")
        self.decimal_entry = ctk.CTkEntry(self.frame, width=150)
        self.decimal_entry.insert(0, "6")
        self.decimal_entry.grid(row=5, column=1, pady=5)

        self.stop_var = ctk.StringVar(value="Epsilon")
        ctk.CTkRadioButton(self.frame, text="By Epsilon", variable=self.stop_var, value="Epsilon", text_color=self.theme["text"]).grid(row=6, column=0, pady=5)
        ctk.CTkRadioButton(self.frame, text="By Iter", variable=self.stop_var, value="Iterations", text_color=self.theme["text"]).grid(row=6, column=1, pady=5)

        ctk.CTkButton(self.frame, text="Solve", command=self.on_solve, fg_color=self.theme["button"], 
                     hover_color=self.theme["button_hover"]).grid(row=7, column=0, columnspan=2, pady=10)

    def update_fields(self, method: str):
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.entries = {}
        if method in ["Bisection", "False Position"]:
            ctk.CTkLabel(self.input_frame, text="Xl:", text_color=self.theme["text"]).grid(row=0, column=0, pady=5, padx=10, sticky="e")
            self.entries["xl"] = ctk.CTkEntry(self.input_frame, width=150)
            self.entries["xl"].grid(row=0, column=1, pady=5)
            ctk.CTkLabel(self.input_frame, text="Xu:", text_color=self.theme["text"]).grid(row=1, column=0, pady=5, padx=10, sticky="e")
            self.entries["xu"] = ctk.CTkEntry(self.input_frame, width=150)
            self.entries["xu"].grid(row=1, column=1, pady=5)
        elif method in ["Fixed Point", "Newton-Raphson"]:
            ctk.CTkLabel(self.input_frame, text="Xi:", text_color=self.theme["text"]).grid(row=0, column=0, pady=5, padx=10, sticky="e")
            self.entries["xi"] = ctk.CTkEntry(self.input_frame, width=150)
            self.entries["xi"].grid(row=0, column=1, pady=5)
        elif method == "Secant":
            ctk.CTkLabel(self.input_frame, text="Xi-1:", text_color=self.theme["text"]).grid(row=0, column=0, pady=5, padx=10, sticky="e")
            self.entries["xi_minus_1"] = ctk.CTkEntry(self.input_frame, width=150)
            self.entries["xi_minus_1"].grid(row=0, column=1, pady=5)
            ctk.CTkLabel(self.input_frame, text="Xi:", text_color=self.theme["text"]).grid(row=1, column=0, pady=5, padx=10, sticky="e")
            self.entries["xi"] = ctk.CTkEntry(self.input_frame, width=150)
            self.entries["xi"].grid(row=1, column=1, pady=5)

    def validate_input(self) -> tuple[bool, str]:
        """Validate all input fields and return (is_valid, error_message)."""
        try:
            # Validate function
            func = self.func_entry.get().strip()
            if not func:
                return False, "Function cannot be empty"

            # Validate epsilon
            try:
                eps = float(self.eps_entry.get() or "0.0001")
                if eps <= 0:
                    return False, "Epsilon must be positive"
            except ValueError:
                return False, "Epsilon must be a number"

            # Validate max iterations
            try:
                max_iter = int(self.iter_entry.get() or "50")
                if max_iter <= 0:
                    return False, "Maximum iterations must be positive"
            except ValueError:
                return False, "Maximum iterations must be an integer"

            # Validate decimal places
            try:
                decimal_places = int(self.decimal_entry.get() or "6")
                if decimal_places < 0:
                    return False, "Decimal places must be non-negative"
            except ValueError:
                return False, "Decimal places must be an integer"

            # Validate method-specific parameters
            method = self.method_var.get()
            params = {}
            for key, entry in self.entries.items():
                try:
                    value = float(entry.get() or "0")
                    params[key] = value
                except ValueError:
                    return False, f"Invalid value for {key}"

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
            max_iter = int(self.iter_entry.get() or "50")
            decimal_places = int(self.decimal_entry.get() or "6")
            stop_by_eps = self.stop_var.get() == "Epsilon"
            params = {key: float(entry.get() or "0") for key, entry in self.entries.items()}
            self.solve_callback(func, method, params, eps, max_iter, stop_by_eps, decimal_places)
        except Exception as e:
            self.logger.error(f"Error in solve callback: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_theme(self, theme: dict):
        self.theme = theme
        self.frame.configure(fg_color=theme["bg"])
        self.input_frame.configure(fg_color=theme["bg"])
        for w in self.frame.winfo_children():
            if isinstance(w, ctk.CTkLabel):
                w.configure(text_color=theme["text"])
            elif isinstance(w, (ctk.CTkButton, ctk.CTkOptionMenu)):
                w.configure(fg_color=theme["button"], hover_color=theme["button_hover"])
            elif isinstance(w, ctk.CTkRadioButton):
                w.configure(text_color=theme["text"])