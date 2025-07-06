from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.barcode import code128
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from typing import List, Dict, Any
import os
import io
from .label_formats import LabelFormat


class PDFGeneratorBarcode:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_labels(self, data: List[Dict[str, Any]], label_format: LabelFormat, 
                       output_filename: str) -> str:
        """Generate labels with barcode, SKU text, price, and case quantity. Repeat based on quantity."""
        output_path = os.path.join(self.output_dir, output_filename)
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Page dimensions
        page_width, page_height = letter
        
        # Expand data based on quantity
        expanded_data = []
        for item in data:
            quantity = int(item.get('quantity', 1))
            for _ in range(quantity):
                expanded_data.append(item)
        
        # Generate labels
        label_index = 0
        total_labels = len(expanded_data)
        
        while label_index < total_labels:
            # Draw labels for current page
            for row in range(label_format.rows):
                for col in range(label_format.columns):
                    if label_index >= total_labels:
                        break
                    
                    # Calculate position
                    x = label_format.margin_left * inch + \
                        col * (label_format.width * inch + label_format.horizontal_spacing * inch)
                    y = page_height - label_format.margin_top * inch - \
                        (row + 1) * label_format.height * inch - \
                        row * label_format.vertical_spacing * inch
                    
                    # Draw label
                    self._draw_barcode_label(c, x, y, label_format.width * inch, 
                                           label_format.height * inch, expanded_data[label_index])
                    
                    label_index += 1
            
            # Start new page if more labels remain
            if label_index < total_labels:
                c.showPage()
        
        c.save()
        return output_path
    
    def _get_optimal_font_size(self, canvas_obj, text, max_width, max_height, font_name="Helvetica-Bold"):
        """Calculate the optimal font size to fit text within given dimensions."""
        # Start with a reasonable size and work down
        for font_size in range(20, 6, -1):
            canvas_obj.setFont(font_name, font_size)
            text_width = canvas_obj.stringWidth(text)
            text_height = font_size * 1.2  # Approximate height including descenders
            
            if text_width <= max_width and text_height <= max_height:
                return font_size
        return 6  # Minimum font size
    
    def _draw_barcode_label(self, canvas_obj: canvas.Canvas, x: float, y: float, 
                           width: float, height: float, item_data: Dict[str, Any]):
        """Draw a label with barcode at top, SKU text, price, and case quantity."""
        
        # Get data and convert to uppercase
        sku = str(item_data.get('sku', '')).upper()
        price = item_data.get('price', 0)
        case_qty = item_data.get('case_qty', 1)
        
        # Format price
        if isinstance(price, (int, float)):
            price_text = f"${price:.2f}"
        else:
            price_text = str(price).upper()
        
        # Format case quantity
        case_text = f"Case: {case_qty}"
        
        # Layout calculations with better spacing for 4 elements
        padding = 0.04 * inch
        element_spacing = 0.02 * inch
        
        # Four sections: barcode, SKU, price, case quantity
        barcode_height = height * 0.35   # 35% for barcode
        sku_height = height * 0.25       # 25% for SKU
        price_height = height * 0.25     # 25% for price
        case_height = height * 0.15      # 15% for case quantity
        
        # Available text areas (minus padding and spacing)
        text_width = width - (2 * padding)
        sku_text_height = sku_height - element_spacing
        price_text_height = price_height - element_spacing
        case_text_height = case_height - element_spacing
        
        # Draw barcode at top (centered)
        if sku and len(sku) > 0:
            try:
                # Create barcode with appropriate sizing
                barcode_draw_height = min(barcode_height * 0.8, 0.35 * inch)  # Max 0.35 inch
                barcode = code128.Code128(sku, barHeight=barcode_draw_height, barWidth=0.6)
                
                # Get actual barcode dimensions
                barcode_width = barcode.width
                max_barcode_width = text_width
                
                # Scale down if too wide
                if barcode_width > max_barcode_width:
                    scale_factor = max_barcode_width / barcode_width
                    barcode.barWidth = barcode.barWidth * scale_factor
                    barcode_width = barcode.width
                
                # Center the barcode horizontally and vertically in its section
                barcode_x = x + (width - barcode_width) / 2
                barcode_y = y + price_height + sku_height + case_height + (barcode_height - barcode_draw_height) / 2
                
                # Draw the barcode
                barcode.drawOn(canvas_obj, barcode_x, barcode_y)
                
            except Exception as e:
                # If barcode fails, draw a placeholder
                placeholder_font_size = self._get_optimal_font_size(canvas_obj, f"BARCODE: {sku}", text_width, barcode_height * 0.8)
                canvas_obj.setFont("Helvetica", placeholder_font_size)
                canvas_obj.drawCentredString(x + width/2, y + price_height + sku_height + case_height + barcode_height/2, f"BARCODE: {sku}")
        
        # Draw SKU text (centered, auto-sized)
        sku_font_size = self._get_optimal_font_size(canvas_obj, sku, text_width, sku_text_height)
        canvas_obj.setFont("Helvetica-Bold", sku_font_size)
        sku_y = y + price_height + case_height + (sku_height/2)
        canvas_obj.drawCentredString(x + width/2, sku_y, sku)
        
        # Draw price (centered, auto-sized)
        price_font_size = self._get_optimal_font_size(canvas_obj, price_text, text_width, price_text_height)
        canvas_obj.setFont("Helvetica-Bold", price_font_size)
        price_y = y + case_height + (price_height/2)
        canvas_obj.drawCentredString(x + width/2, price_y, price_text)
        
        # Draw case quantity at bottom (centered, smaller font)
        case_font_size = self._get_optimal_font_size(canvas_obj, case_text, text_width, case_text_height, "Helvetica")
        canvas_obj.setFont("Helvetica", case_font_size)
        case_y = y + (case_height/2)
        canvas_obj.drawCentredString(x + width/2, case_y, case_text)
        
        # Optional: Draw border for debugging
        # canvas_obj.rect(x, y, width, height)