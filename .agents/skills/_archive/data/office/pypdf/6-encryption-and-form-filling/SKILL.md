---
name: pypdf-6-encryption-and-form-filling
description: 'Sub-skill of pypdf: 6. Encryption and Form Filling.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 6. Encryption and Form Filling

## 6. Encryption and Form Filling


```python
"""
PDF encryption, decryption, and form handling.
"""
from pypdf import PdfReader, PdfWriter
from pathlib import Path
from typing import Dict, Optional, List

def encrypt_pdf(
    input_path: str,
    output_path: str,
    user_password: str,
    owner_password: Optional[str] = None,
    permissions: Optional[Dict[str, bool]] = None
) -> None:
    """Encrypt PDF with password protection.

    Args:
        input_path: Source PDF file
        output_path: Destination file
        user_password: Password to open the document
        owner_password: Password for full access (defaults to user_password)
        permissions: Dict of permission flags (print, modify, copy, etc.)
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Copy metadata if exists
    if reader.metadata:
        writer.add_metadata(reader.metadata)

    # Default permissions (restrictive)
    default_permissions = {
        'print': True,
        'modify': False,
        'copy': False,
        'annotations': True,
        'forms': True,
        'extract': False,
        'assemble': False,
        'print_high_quality': True
    }

    if permissions:
        default_permissions.update(permissions)

    # Encrypt
    owner_pwd = owner_password or user_password
    writer.encrypt(
        user_password=user_password,
        owner_password=owner_pwd,
        permissions_flag=-1  # All permissions by default
    )

    writer.write(output_path)
    print(f"Encrypted PDF saved to: {output_path}")


def decrypt_pdf(
    input_path: str,
    output_path: str,
    password: str
) -> bool:
    """Decrypt a password-protected PDF.

    Args:
        input_path: Encrypted PDF file
        output_path: Destination file (unencrypted)
        password: Password to decrypt

    Returns:
        True if successful, False otherwise
    """
    try:
        reader = PdfReader(input_path)

        if reader.is_encrypted:
            if not reader.decrypt(password):
                print("Incorrect password")
                return False

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        if reader.metadata:
            writer.add_metadata(reader.metadata)

        writer.write(output_path)
        print(f"Decrypted PDF saved to: {output_path}")
        return True

    except Exception as e:
        print(f"Decryption failed: {e}")
        return False


def get_form_fields(input_path: str) -> Dict[str, Dict]:
    """Get all form fields from a PDF."""
    reader = PdfReader(input_path)
    fields = {}

    if reader.get_fields():
        for name, field in reader.get_fields().items():
            field_type = field.get('/FT', '')
            value = field.get('/V', '')

            fields[name] = {
                'type': str(field_type),
                'value': str(value) if value else '',
                'field': field
            }

    return fields


def fill_pdf_form(
    input_path: str,
    output_path: str,
    field_values: Dict[str, str],
    flatten: bool = False
) -> None:
    """Fill PDF form fields with values.

    Args:
        input_path: Source PDF with form fields
        output_path: Destination file
        field_values: Dictionary of field names and values
        flatten: If True, make form fields uneditable
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Add pages
    for page in reader.pages:
        writer.add_page(page)

    # Update form fields
    writer.update_page_form_field_values(
        writer.pages[0] if writer.pages else None,
        field_values
    )

    if flatten:
        # Note: Full flatten support may require additional processing
        for page in writer.pages:
            if '/Annots' in page:
                del page['/Annots']

    writer.write(output_path)
    print(f"Form filled and saved to: {output_path}")


def list_form_fields_report(input_path: str) -> str:
    """Generate a report of all form fields in a PDF."""
    fields = get_form_fields(input_path)

    if not fields:
        return "No form fields found in this PDF."

    report = ["PDF Form Fields Report", "=" * 40, ""]

    for name, info in fields.items():
        report.append(f"Field: {name}")
        report.append(f"  Type: {info['type']}")
        report.append(f"  Current Value: {info['value'] or '(empty)'}")
        report.append("")

    report.append(f"Total fields: {len(fields)}")

    return "\n".join(report)


# Example usage
# encrypt_pdf('document.pdf', 'encrypted.pdf', 'mypassword')
# decrypt_pdf('encrypted.pdf', 'decrypted.pdf', 'mypassword')
#
# fields = get_form_fields('form.pdf')
# fill_pdf_form('form.pdf', 'filled_form.pdf', {
#     'name': 'John Doe',
#     'date': '2026-01-17',

*Content truncated — see parent skill for full reference.*
