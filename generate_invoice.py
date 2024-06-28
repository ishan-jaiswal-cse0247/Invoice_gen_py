import os
import json
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import inflect
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_file='config.json'):
    with open(config_file, 'r') as f:
        return json.load(f)

def validate_data(data):
    required_fields = [
        'logo_url', 'seller_name', 'seller_address', 'seller_city', 'seller_state', 'seller_pincode',
        'seller_pan', 'seller_gst', 'billing_name', 'billing_address', 'billing_city', 'billing_state',
        'billing_pincode', 'billing_state_code', 'shipping_name', 'shipping_address', 'shipping_city',
        'shipping_state', 'shipping_pincode', 'shipping_state_code', 'order_no', 'order_date',
        'invoice_no', 'invoice_date', 'reverse_charge', 'place_of_supply', 'place_of_delivery', 'items',
        'signature_url'
    ]

    for field in required_fields:
        if field not in data:
            raise ValueError(f'Missing required field: {field}')

    # Validate dates
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    if not re.match(date_pattern, data['order_date']):
        raise ValueError('Invalid order date format. Expected YYYY-MM-DD.')
    if not re.match(date_pattern, data['invoice_date']):
        raise ValueError('Invalid invoice date format. Expected YYYY-MM-DD.')

    # Validate numerical fields
    if not isinstance(data['items'], list) or len(data['items']) == 0:
        raise ValueError('Items must be a non-empty list.')

    for item in data['items']:
        if not isinstance(item['unit_price'], (int, float)) or item['unit_price'] < 0:
            raise ValueError('Invalid unit price in items.')
        if not isinstance(item['quantity'], int) or item['quantity'] <= 0:
            raise ValueError('Invalid quantity in items.')
        if not isinstance(item['discount'], (int, float)) or item['discount'] < 0:
            raise ValueError('Invalid discount in items.')
        if not isinstance(item['tax_rate'], (int, float)) or item['tax_rate'] < 0:
            raise ValueError('Invalid tax rate in items.')

def generate_invoice(data, config):
    try:
        # Validate input data
        validate_data(data)

        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(os.path.dirname(config['template_path'])))
        template = env.get_template(os.path.basename(config['template_path']))

        # Compute derived fields
        total_amount = 0
        for item in data['items']:
            item['net_amount'] = item['unit_price'] * item['quantity'] - item['discount']
            if data['place_of_supply'] == data['place_of_delivery']:
                item['cgst_amount'] = item['net_amount'] * (item['tax_rate'] / 2) / 100
                item['sgst_amount'] = item['net_amount'] * (item['tax_rate'] / 2) / 100
                item['igst_amount'] = 0
            else:
                item['cgst_amount'] = 0
                item['sgst_amount'] = 0
                item['igst_amount'] = item['net_amount'] * item['tax_rate'] / 100
            item['total_amount'] = item['net_amount'] + item['cgst_amount'] + item['sgst_amount'] + item['igst_amount']
            total_amount += item['total_amount']

        data['total_amount'] = total_amount

        # Convert amount to words
        p = inflect.engine()
        data['amount_in_words'] = p.number_to_words(total_amount).capitalize()

        # Render HTML template with data
        html_out = template.render(data)

        # Save HTML to a file
        with open(config['output_html'], 'w') as f:
            f.write(html_out)

        # Convert HTML to PDF
        HTML(config['output_html']).write_pdf(config['output_pdf'])

        logging.info('Invoice generated successfully.')

    except Exception as e:
        logging.error(f'Error generating invoice: {e}')

if __name__ == '__main__':
    # Load configuration
    config = load_config()

    # Sample data for testing
    data = {
        "logo_url": "https://example.com/logo.png",
        "seller_name": "Example Seller",
        "seller_address": "123 Seller St.",
        "seller_city": "Seller City",
        "seller_state": "Seller State",
        "seller_pincode": "123456",
        "seller_pan": "ABCDE1234F",
        "seller_gst": "12ABCDE1234F1Z5",
        "billing_name": "Customer Name",
        "billing_address": "456 Billing St.",
        "billing_city": "Billing City",
        "billing_state": "Billing State",
        "billing_pincode": "654321",
        "billing_state_code": "12",
        "shipping_name": "Customer Name",
        "shipping_address": "789 Shipping St.",
        "shipping_city": "Shipping City",
        "shipping_state": "Shipping State",
        "shipping_pincode": "987654",
        "shipping_state_code": "34",
        "order_no": "ORD123",
        "order_date": "2024-01-01",
        "invoice_no": "INV123",
        "invoice_date": "2024-01-02",
        "reverse_charge": "No",
        "place_of_supply": "Seller State",
        "place_of_delivery": "Seller State",
        "items": [
            {
                "description": "Item 1",
                "unit_price": 100.00,
                "quantity": 2,
                "discount": 10.00,
                "tax_rate": 18
            },
            {
                "description": "Item 2",
                "unit_price": 200.00,
                "quantity": 1,
                "discount": 0.00,
                "tax_rate": 18
            }
        ],
        "signature_url": "https://example.com/signature.png"
    }

    generate_invoice(data, config)
