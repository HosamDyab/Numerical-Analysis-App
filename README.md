# Numerical Analysis Application

A modern, user-friendly application for solving numerical analysis problems with a beautiful UI and robust error handling.

## Features

- **Multiple Numerical Methods**: Supports various root-finding methods including:
  - Bisection Method
  - False Position Method
  - Fixed Point Method
  - Newton-Raphson Method
  - Secant Method

- **User-Friendly Interface**:
  - Modern, responsive UI built with CustomTkinter
  - Light and dark theme support
  - Intuitive input forms
  - Real-time results display

- **Advanced Features**:
  - Solution history tracking
  - PDF export functionality
  - Customizable precision settings
  - Automatic error handling
  - User preferences management

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/numerical-analysis-app.git
   cd numerical-analysis-app
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```
   python main.py
   ```

2. Select a numerical method from the sidebar.

3. Enter the function and required parameters.

4. Click "Solve" to calculate the root.

5. View the results in the table and optionally export to PDF.

## Configuration

The application supports various user preferences that can be customized:

- Theme (light/dark/system)
- Decimal places precision
- Maximum iterations
- Epsilon value
- Auto-save settings
- Window size

Preferences are stored in `user_preferences.json` and can be modified through the application's settings menu.

## Error Handling

The application includes comprehensive error handling for:

- Invalid function expressions
- Out-of-range parameters
- Convergence issues
- File I/O operations
- User input validation

## Development

### Project Structure

```
numerical-analysis-app/
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
├── src/
│   ├── core/               # Core numerical methods
│   │   ├── methods/        # Implementation of each method
│   │   ├── solver.py       # Main solver class
│   │   └── history.py      # History management
│   ├── ui/                 # User interface
│   │   ├── widgets/        # UI components
│   │   ├── app.py          # Main application class
│   │   └── theme.py        # Theme management
│   └── utils/              # Utility functions
│       ├── export.py       # PDF export functionality
│       └── preferences.py  # User preferences management
├── tests/                  # Test suite
└── docs/                   # Documentation
```

### Running Tests

```
python -m pytest tests/
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI components
- [SymPy](https://www.sympy.org/) for symbolic mathematics
- [NumPy](https://numpy.org/) for numerical computations
- [Matplotlib](https://matplotlib.org/) for plotting capabilities
- [ReportLab](https://www.reportlab.com/) for PDF generation 