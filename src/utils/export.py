from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from typing import List, Dict, Any
import logging
import os

def export_to_pdf(filename: str, func: str, method: str, root: float, table_data: List[Dict[str, Any]]) -> None:
    """
    Export solution to a PDF file with error handling.
    
    Args:
        filename: Name of the output PDF file
        func: The mathematical function
        method: The numerical method used
        root: The calculated root
        table_data: List of dictionaries containing iteration details
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Add header information
        elements.append(Paragraph(
            f"Numerical Analysis Report<br/>"
            f"Function: {func}<br/>"
            f"Method: {method}<br/>"
            f"Root: {root}",
            styles["Heading1"]
        ))

        # Prepare table data
        if not table_data:
            data = [["Message"], ["No data available"]]
        elif "Error" in table_data[0]:
            data = [["Message"], [table_data[0].get("Error", "Unknown error")]]
        else:
            headers = list(table_data[0].keys())
            data = [headers] + [[row[col] for col in headers] for row in table_data]
        
        # Create and style the table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)

        # Build the PDF
        doc.build(elements)
        logger.info(f"Successfully exported to {filename}")
        
    except Exception as e:
        logger.error(f"Error exporting to PDF: {str(e)}")
        raise