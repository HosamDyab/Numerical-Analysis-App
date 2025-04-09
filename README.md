# Numerical Analysis Application

A comprehensive Python application for solving numerical analysis problems, featuring multiple root-finding methods with a modern GUI interface.

![Application Screenshot](docs/images/screenshot.png)

## Features

- **Multiple Numerical Methods**:
  - Bisection Method
  - False Position Method
  - Fixed Point Method
  - Newton-Raphson Method
  - Secant Method

- **Modern GUI Interface**:
  - Clean and intuitive design
  - Dark/Light theme support
  - Real-time results
  - Interactive function plotting

- **Advanced Features**:
  - Detailed iteration tables
  - Error analysis
  - Export to PDF
  - History tracking
  - Customizable settings

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NumericalAnalysisApp.git
cd NumericalAnalysisApp
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Select a numerical method from the dropdown menu
3. Enter your function (e.g., "x**2 - 4")
4. Input the required parameters
5. Click "Solve" to get results

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Testing

Run the test suite:
```bash
python -m unittest discover tests
```

## Documentation

Detailed documentation is available in the [docs](docs/) directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and CustomTkinter
- Inspired by numerical analysis courses
- Thanks to all contributors

## Contact

For questions or suggestions, please open an issue on GitHub. 