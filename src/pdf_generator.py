from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from typing import List, Dict, Any
import os
from .label_formats import LabelFormat


class PDFGenerator:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_labels(self, data: List[Dict[str, Any]], label_format: LabelFormat, 
                       output_filename: str, fields_config: Dict[str, str]) -> str:
        output_path = os.path.join(self.output_dir, output_filename)
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Page dimensions
        page_width, page_height = letter
        
        # Calculate label positions
        label_index = 0
        total_labels = len(data)
        
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
                    self._draw_label(c, x, y, label_format.width * inch, 
                                   label_format.height * inch, data[label_index], fields_config)
                    
                    label_index += 1
            
            # Start new page if more labels remain
            if label_index < total_labels:
                c.showPage()
        
        c.save()
        return output_path
    
    def _draw_label(self, canvas_obj: canvas.Canvas, x: float, y: float, 
                   width: float, height: float, item_data: Dict[str, Any], 
                   fields_config: Dict[str, str]):
        # Draw border (optional, for debugging)
        # canvas_obj.rect(x, y, width, height)
        
        # Get field mappings
        product_field = fields_config.get('product', 'product')
        price_field = fields_config.get('price', 'price')
        sku_field = fields_config.get('sku', 'sku')
        
        # Content
        y_offset = y + height - 0.2 * inch
        
        # Product name
        if product_field in item_data:
            product_name = str(item_data[product_field])
            canvas_obj.drawCentredString(x + width/2, y_offset, product_name[:30])
            y_offset -= 0.3 * inch
        
        # Price
        if price_field in item_data:
            price = item_data[price_field]
            if isinstance(price, (int, float)):
                price_text = f"${price:.2f}"
            else:
                price_text = str(price)
            canvas_obj.setFont("Helvetica-Bold", 16)
            canvas_obj.drawCentredString(x + width/2, y_offset, price_text)
            canvas_obj.setFont("Helvetica", 10)
            y_offset -= 0.3 * inch
        
        # SKU
        if sku_field in item_data and y_offset > y:
            sku = str(item_data[sku_field])
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.drawCentredString(x + width/2, y_offset, f"SKU: {sku}")
            canvas_obj.setFont("Helvetica", 10)