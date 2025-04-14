# Numerical Analysis Application

A comprehensive Python application for solving numerical analysis problems, featuring multiple root-finding methods and linear system solvers with a modern GUI interface.


## Features

- **Root-Finding Methods**:
  - Bisection Method
  - False Position Method
  - Fixed Point Method
  - Newton-Raphson Method
  - Secant Method

- **Linear System Solvers**:
  - Gauss Elimination
  - Gauss Elimination with Partial Pivoting
  - LU Decomposition
  - LU Decomposition with Partial Pivoting
  - Gauss-Jordan Method
  - Gauss-Jordan Method with Partial Pivoting

- **Modern GUI Interface**:
  - Clean and intuitive design
  - Dark/Light theme support
  - Real-time results
  - Interactive function plotting

- **Advanced Features**:
  - Detailed iteration tables
  - Step-by-step solution process
  - Error analysis
  - Export to PDF
  - History tracking
  - Customizable settings

## Installation

1. Clone the repository:
```bash
git clone https://github.com/HosamDyab/NumericalAnalysisApp.git
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
3. Enter the required parameters:
   - For root-finding methods: function, bounds/initial values, and convergence criteria
   - For linear systems: coefficient matrix and right-hand side vector
4. Click "Solve" to compute the solution
5. View the detailed solution steps and results

## Methods Implementation

### Root-Finding Methods
- **Bisection Method**: Finds roots by repeatedly bisecting an interval
- **False Position Method**: Linear interpolation between function values
- **Fixed Point Method**: Iterative application of a function until convergence
- **Newton-Raphson Method**: Uses derivative information for faster convergence
- **Secant Method**: Approximates derivatives using finite differences

### Linear System Solvers
- **Gauss Elimination**: Forward elimination to create an upper triangular matrix, followed by back-substitution
- **Gauss Elimination with Partial Pivoting**: Enhanced stability through row pivoting
- **LU Decomposition**: Factorizes the coefficient matrix into lower and upper triangular matrices
- **LU Decomposition with Partial Pivoting**: Improved numerical stability for LU factorization
- **Gauss-Jordan Method**: Complete elimination to transform the coefficient matrix into the identity matrix
- **Gauss-Jordan Method with Partial Pivoting**: Enhanced stability for the Gauss-Jordan method

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Developed by Hosam Dyab
- Based on numerical analysis algorithms and techniques