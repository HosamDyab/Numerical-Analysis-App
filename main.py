from src.ui.app import NumericalApp
import sys
import traceback

def main():
    try:
        app = NumericalApp()
        app.run()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()