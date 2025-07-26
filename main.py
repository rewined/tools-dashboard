import click
import os
from src.csv_parser import CSVParser
from src.pdf_generator import PDFGenerator
from src.label_formats import LABEL_FORMATS


@click.command()
@click.option('--input', '-i', 'input_file', required=True, type=click.Path(exists=True),
              help='Path to the input CSV file')
@click.option('--output', '-o', 'output_file', default='labels.pdf',
              help='Output PDF filename (default: labels.pdf)')
@click.option('--format', '-f', 'label_format', type=click.Choice(list(LABEL_FORMATS.keys())),
              default='avery_5160', show_default=True,
              help='Label format to use')
@click.option('--product-field', default='product', show_default=True,
              help='CSV column name for product name')
@click.option('--price-field', default='price', show_default=True,
              help='CSV column name for price')
@click.option('--sku-field', default='sku', show_default=True,
              help='CSV column name for SKU')
@click.option('--list-formats', is_flag=True,
              help='List all available label formats')
def main(input_file, output_file, label_format, product_field, price_field, sku_field, list_formats):
    """
    Price Sticker Printer - Generate formatted PDF labels from CSV data
    """
    
    if list_formats:
        click.echo("\nAvailable label formats:")
        click.echo("-" * 50)
        for key, format_obj in LABEL_FORMATS.items():
            click.echo(f"{key:15} - {format_obj.name}")
        return
    
    click.echo(f"\nProcessing CSV file: {input_file}")
    
    # Parse CSV
    parser = CSVParser(input_file)
    try:
        data = parser.parse()
        click.echo(f"Found {len(data)} items in CSV")
        
        # Show available columns
        columns = parser.get_columns()
        click.echo(f"Available columns: {', '.join(columns)}")
        
        # Validate required columns
        fields_config = {
            'product': product_field,
            'price': price_field,
            'sku': sku_field
        }
        
        # Check if at least product and price fields exist
        missing_fields = []
        if product_field not in columns:
            missing_fields.append(f"product field '{product_field}'")
        if price_field not in columns:
            missing_fields.append(f"price field '{price_field}'")
        
        if missing_fields:
            click.echo(f"\nError: Missing {' and '.join(missing_fields)} in CSV")
            click.echo("Use --product-field and/or --price-field to specify correct column names")
            return
        
    except Exception as e:
        click.echo(f"Error parsing CSV: {str(e)}")
        return
    
    # Generate PDF
    click.echo(f"\nGenerating PDF with format: {LABEL_FORMATS[label_format].name}")
    generator = PDFGenerator()
    
    try:
        output_path = generator.generate_labels(
            data, 
            LABEL_FORMATS[label_format], 
            output_file,
            fields_config
        )
        click.echo(f"\nSuccess! Labels saved to: {output_path}")
        
        # Show summary
        format_obj = LABEL_FORMATS[label_format]
        labels_per_page = format_obj.columns * format_obj.rows
        total_pages = (len(data) + labels_per_page - 1) // labels_per_page
        click.echo(f"Generated {len(data)} labels on {total_pages} page(s)")
        
    except Exception as e:
        click.echo(f"Error generating PDF: {str(e)}")


if __name__ == '__main__':
    main()