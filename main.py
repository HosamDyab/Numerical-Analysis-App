import sys
import traceback
import logging
import os
from src.ui.app import NumericalApp

# Configure logging
def setup_logging():
    """Configure application logging with proper formatting and file handling."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "app.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """Main application entry point with enhanced error handling."""
    logger = setup_logging()
    logger.info("Starting Numerical Analysis Application")
    
    try:
        app = NumericalApp()
        logger.info("Application initialized successfully")
        app.run()
        logger.info("Application terminated normally")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()