import sys
from src.ui.app import NumericalApp
from src.utils.logging_config import configure_logging

def main():
    """Main application entry point."""
    try:
        # Configure logging to suppress warnings
        configure_logging()
        
        # Start the application
        app = NumericalApp()
        app.run()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()