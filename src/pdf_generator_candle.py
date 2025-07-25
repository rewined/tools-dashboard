from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import Image
from typing import List, Dict, Any
import os
import io
import qrcode
from .label_formats import LabelFormat


class PDFGeneratorCandle:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_test_labels(self, test_data: Dict[str, Any], trials: List[Dict[str, Any]], 
                            label_format: LabelFormat, output_filename: str, base_url: str) -> str:
        """Generate candle test labels with QR codes - one label per page for thermal printer."""
        output_path = os.path.join(self.output_dir, output_filename)
        
        # For thermal printer: use custom page size matching label size
        # Standard 1x4" label for thermal printer
        label_width = label_format.width * inch
        label_height = label_format.height * inch
        
        # Create canvas with label size as page size
        c = canvas.Canvas(output_path, pagesize=(label_width, label_height))
        
        # Generate one label per page
        for index, trial in enumerate(trials):
            # Draw label at origin (0, 0) since page size matches label size
            self._draw_candle_test_label(c, 0, 0, label_width, label_height, 
                                       test_data, trial, base_url)
            
            # Create new page for next label (except for the last one)
            if index < len(trials) - 1:
                c.showPage()
        
        c.save()
        return output_path
    
    def _generate_qr_code(self, url: str) -> io.BytesIO:
        """Generate QR code image."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
    
    def _get_optimal_font_size(self, canvas_obj, text, max_width, max_height, font_name="Helvetica"):
        """Calculate the optimal font size to fit text within given dimensions."""
        for font_size in range(12, 4, -1):
            canvas_obj.setFont(font_name, font_size)
            text_width = canvas_obj.stringWidth(text)
            text_height = font_size * 1.2
            
            if text_width <= max_width and text_height <= max_height:
                return font_size
        return 5
    
    def _draw_candle_test_label(self, canvas_obj: canvas.Canvas, x: float, y: float, 
                               width: float, height: float, test_data: Dict[str, Any], 
                               trial: Dict[str, Any], base_url: str):
        """Draw a candle test label with QR code."""
        
        # Layout for 1x4" label on thermal printer
        padding = 0.1 * inch  # More padding for thermal printer
        qr_size = height * 0.75  # QR code takes 75% of height
        
        # Generate QR code URL
        qr_url = f"{base_url}/candle-testing/evaluate/{test_data['id']}/{trial['id']}"
        
        # Draw QR code on the left
        qr_buffer = self._generate_qr_code(qr_url)
        qr_x = x + padding
        qr_y = y + (height - qr_size) / 2
        
        # Create ReportLab Image object
        img = Image(qr_buffer, width=qr_size, height=qr_size)
        img.drawOn(canvas_obj, qr_x, qr_y)
        
        # Text area starts after QR code
        text_x = x + qr_size + padding * 2
        text_width = width - qr_size - padding * 3
        
        # Draw test ID and trial number at top
        canvas_obj.setFont("Helvetica-Bold", 10)
        id_text = f"{test_data['id']}"
        canvas_obj.drawString(text_x, y + height - padding - 12, id_text)
        
        canvas_obj.setFont("Helvetica-Bold", 8)
        trial_text = f"Trial {trial['trial_number']}"
        canvas_obj.drawString(text_x, y + height - padding - 24, trial_text)
        
        # Draw components info
        canvas_obj.setFont("Helvetica", 6)
        component_y = y + height - padding - 36
        
        # Vessel
        vessel_text = test_data['vessel'].split(' - ')[0]  # Just the code
        canvas_obj.drawString(text_x, component_y, f"V: {vessel_text}")
        
        # Wax
        wax_text = test_data['wax'].split(' - ')[0]  # Just the code
        canvas_obj.drawString(text_x, component_y - 9, f"W: {wax_text}")
        
        # Fragrance and blend
        fragrance_text = test_data['fragrance'].split(' - ')[0]  # Just the code
        canvas_obj.drawString(text_x, component_y - 18, f"F: {fragrance_text} @ {test_data['blend_percentage']}%")
        
        # Wick (larger font for emphasis)
        canvas_obj.setFont("Helvetica-Bold", 9)
        wick_text = trial['wick'].replace('Wick.', '').replace('WICK-', '')  # Remove prefixes
        canvas_obj.drawString(text_x, component_y - 30, f"Wick: {wick_text}")
        
        # Optional: Draw border for debugging
        # canvas_obj.rect(x, y, width, height)