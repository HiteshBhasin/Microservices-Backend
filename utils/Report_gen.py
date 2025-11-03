import textwrap
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class DoorLoopReportGenerator:
    """Professional PDF report generator for DoorLoop data with text wrapping and customizable styling."""
    
    def __init__(self, 
                 col_width=5.0,  # Even wider columns
                 row_height=0.9,  # Taller rows for wrapped text
                 font_size=11,  # Larger font size
                 header_font_size=12,
                 max_text_width=40):  # More characters before wrapping
        self.col_width = col_width
        self.row_height = row_height
        self.font_size = font_size
        self.header_font_size = header_font_size
        self.max_text_width = max_text_width
        
    def wrap_text(self, text, width=None):
        """Wrap text to fit within column width."""
        if width is None:
            width = self.max_text_width
            
        if not isinstance(text, str):
            text = str(text)
            
        if len(text) <= width:
            return text
            
        # Use textwrap for clean line breaks
        wrapped_lines = textwrap.wrap(text, width=width, break_long_words=False)
        return '\n'.join(wrapped_lines[:3])  # Limit to 3 lines max
    
    def format_numeric_value(self, value):
        """Format numeric values with proper comma separation - ensure no truncation."""
        if pd.isna(value) or value is None:
            return ""
        elif isinstance(value, (int, float)):
            if value == 0:
                return "0"
            elif isinstance(value, float):
                # For very large numbers, use scientific notation to prevent cutting
                if abs(value) >= 1000000:
                    return f"{value:,.0f}"  # No decimals for large numbers
                else:
                    return f"{value:,.2f}"
            else:
                return f"{value:,}"
        else:
            # Convert to string and ensure it's not too long
            str_val = str(value)
            if len(str_val) > 15:  # If text is very long, wrap it
                return self.wrap_text(str_val, 15)
            return str_val
    
    def prepare_table_data(self, df):
        """Prepare and format table data with text wrapping."""
        table_data = []
        
        for _, row in df.iterrows():
            formatted_row = []
            for i, cell in enumerate(row):
                # Format ALL cells properly to prevent cutting
                if isinstance(cell, (int, float)) and not pd.isna(cell):
                    # Always use numeric formatting for numbers
                    formatted_cell = self.format_numeric_value(cell)
                else:
                    # For text, wrap if needed
                    if isinstance(cell, str) and len(cell) > self.max_text_width:
                        formatted_cell = self.wrap_text(cell, self.max_text_width)
                    else:
                        formatted_cell = self.wrap_text(str(cell), self.max_text_width)
                
                formatted_row.append(formatted_cell)
            table_data.append(formatted_row)
        
        return table_data
    
    def prepare_column_headers(self, df):
        """Prepare column headers with wrapping."""
        headers = []
        for col in df.columns:
            # Clean up column names
            clean_col = str(col).replace('_', ' ').title()
            # Wrap long headers
            wrapped_header = self.wrap_text(clean_col, 25)  # More space for headers
            headers.append(wrapped_header)
        return headers
    
    def calculate_column_widths(self, df):
        """Calculate UNIFORM column widths - all columns same width but WIDER."""
        num_cols = len(df.columns)
        
        # Make all columns even wider to prevent any cutting
        uniform_width = 0.28  # Increased from 0.22 to 0.28 for more space
        col_widths = [uniform_width] * num_cols  # Create list with same width for all columns
        
        return col_widths
    
    def style_table(self, table, df, col_widths):
        """Apply styling to the matplotlib table."""
        num_rows, num_cols = len(df), len(df.columns)
        
        # Apply column widths and row heights
        for i in range(num_cols):
            for j in range(num_rows + 1):  # +1 for header
                cell = table[(j, i)]
                cell.set_width(col_widths[i])  # All columns now have same width
                cell.set_height(0.15)  # Even taller rows for better spacing
                
                # Add padding to prevent text cutting
                cell.PAD = 0.05  # More internal padding
                
                # Header row styling
                if j == 0:
                    cell.set_facecolor('#2E75B6')
                    cell.set_text_props(
                        weight='bold', 
                        color='white', 
                        fontsize=self.header_font_size,
                        verticalalignment='center',
                        ha='center'  # Center align headers for uniform look
                    )
                else:
                    # Data row styling
                    if j % 2 == 0:
                        cell.set_facecolor('#F8F9FA')
                    else:
                        cell.set_facecolor('white')
                    
                    # Set text properties for data cells - all left aligned for consistency
                    cell.set_text_props(
                        ha='left',  # All columns left-aligned for uniform appearance
                        fontsize=self.font_size,
                        verticalalignment='center'
                    )
        
        return table
    
    def generate_pdf(self, df, filename="Report.pdf", title="Nest Host Financial Report"):
        """Generate a professional PDF report from DataFrame."""
        if not hasattr(df, 'values') or not hasattr(df, 'columns'):
            raise ValueError("Input must be a pandas DataFrame")
        
        num_cols = len(df.columns)
        num_rows = len(df)
        
        # Calculate figure dimensions with wider layout to prevent cutting
        fig_width = max(28, num_cols * self.col_width)  # Much wider base (was 24)
        fig_height = max(18, num_rows * self.row_height + 7)  # Taller figure (was 16)
        
        with PdfPages(filename) as pdf:
            fig = plt.figure(figsize=(fig_width, fig_height))
            ax = fig.add_subplot(111)
            ax.axis('off')
            
            # Prepare data
            table_data = self.prepare_table_data(df)
            headers = self.prepare_column_headers(df)
            col_widths = self.calculate_column_widths(df)
            
            # Create table
            table = ax.table(
                cellText=table_data,
                colLabels=headers,
                cellLoc='left',
                loc='center',
                bbox=[0, 0, 1, 0.72]  # More space for title and margins
            )
            
            # Style the table
            table.auto_set_font_size(False)
            self.style_table(table, df, col_widths)
            
            # Add title with Nest Host company branding
            fig.suptitle(title, fontsize=26, fontweight='bold', y=0.95)
            
            # Add company name and subtitle
            plt.figtext(0.5, 0.88, 
                       f'Nest Host | Generated on {pd.Timestamp.now().strftime("%B %d, %Y")} | {num_rows} entries', 
                       ha='center', fontsize=18, style='italic')
            
            # Save with high quality
            pdf.savefig(fig, bbox_inches='tight', dpi=300, 
                       facecolor='white', edgecolor='none')
            plt.close(fig)
        
        return {
            "filename": filename,
            "rows": num_rows,
            "columns": num_cols,
            "figure_size": f"{fig_width:.1f}\" × {fig_height:.1f}\"",
            "status": "success"
        }


    