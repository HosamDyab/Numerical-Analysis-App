from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import List, Dict, Any, Optional
import logging
import os
import re
from datetime import datetime

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to make it safe for all operating systems.
    
    Args:
        filename: The original filename
        
    Returns:
        A sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    return sanitized

def format_table_data(table_data: List[Dict[str, Any]]) -> List[List[str]]:
    """
    Format table data for PDF export with proper handling of different data types.
    
    Args:
        table_data: List of dictionaries containing iteration details
        
    Returns:
        Formatted table data as a list of lists
    """
    if not table_data:
        return [["Message"], ["No data available"]]
        
    if "Error" in table_data[0]:
        return [["Message"], [table_data[0].get("Error", "Unknown error")]]
        
    # Get headers from the first row
    headers = list(table_data[0].keys())
    
    # Format each row
    formatted_data = [headers]
    for row in table_data:
        formatted_row = []
        for header in headers:
            value = row.get(header, "")
            # Format numbers to a reasonable precision
            if isinstance(value, (int, float)):
                formatted_row.append(f"{value:.6f}")
            else:
                formatted_row.append(str(value))
        formatted_data.append(formatted_row)
        
    return formatted_data

def export_to_pdf(filename: str, func: str, method: str, root: float, table_data: List[Dict[str, Any]]) -> bool:
    """
    Export solution to a PDF file with enhanced error handling and formatting.
    
    Args:
        filename: Name of the output PDF file
        func: The mathematical function
        method: The numerical method used
        root: The calculated root
        table_data: List of dictionaries containing iteration details
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Sanitize and validate filename
        sanitized_filename = sanitize_filename(filename)
        if not sanitized_filename.endswith('.pdf'):
            sanitized_filename += '.pdf'
            
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(sanitized_filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # Create the PDF document
        doc = SimpleDocTemplate(
            sanitized_filename, 
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Prepare elements for the PDF
        elements = []
        styles = getSampleStyleSheet()
        
        # Add custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12
        ))
        
        # Add title
        elements.append(Paragraph("Numerical Analysis Report", styles["CustomTitle"]))
        elements.append(Spacer(1, 0.25*inch))
        
        # Add metadata
        elements.append(Paragraph(f"<b>Function:</b> {func}", styles["CustomBody"]))
        elements.append(Paragraph(f"<b>Method:</b> {method}", styles["CustomBody"]))
        elements.append(Paragraph(f"<b>Root:</b> {root:.6f}", styles["CustomBody"]))
        elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["CustomBody"]))
        elements.append(Spacer(1, 0.25*inch))
        
        # Add table
        elements.append(Paragraph("Iteration Results", styles["Heading2"]))
        elements.append(Spacer(1, 0.1*inch))
        
        # Format and create table
        data = format_table_data(table_data)
        table = Table(data)
        
        # Style the table
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            
            # Zebra striping for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(table)
        
        # Build the PDF
        doc.build(elements)
        logger.info(f"Successfully exported to {sanitized_filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to PDF: {str(e)}")
        return False