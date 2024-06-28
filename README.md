# Invoice Generator

This project generates invoices for orders placed on an e-commerce platform. It creates invoices in HTML and PDF formats, featuring customizable seller, billing, and shipping details, as well as detailed item information.

## Features

- Company logo placeholder
- Seller, billing, and shipping details
- Order and invoice details
- Reverse charge option
- Item details with tax calculations
- Signature inclusion
- Total amount in words
- PDF generation

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/invoice_generator.git
   cd invoice_generator
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

Update `config.json` with template and output file paths:

```json
{
  "template_path": "templates/invoice_template.html",
  "output_html": "invoice.html",
  "output_pdf": "invoice.pdf"
}
```
