import fitz  # PyMuPDF
import os

def list_pdf_form_fields(pdf_path: str) -> list[str]:
    """
    Inspects a PDF file and returns a list of its fillable form field names.
    Args:
        pdf_path: The local path to the PDF file.
    Returns:
        A list of strings, where each string is the fully qualified name of a form field.
    """
    try:
        doc = fitz.open(pdf_path)
        fields = []
        for page in doc:
            for field in page.widgets():
                fields.append(field.field_name)
        doc.close()
        if not fields:
            return ["No fillable form fields were found in this document."]
        return fields
    except Exception as e:
        return [f"An error occurred while processing the PDF: {str(e)}"]

def fill_pdf_form_field(pdf_path: str, field_name: str, value: str) -> str:
    """
    Fills a specific form field in a PDF with a given value and saves a new file.
    Args:
        pdf_path: The local path to the original PDF file.
        field_name: The name of the form field to fill.
        value: The text value to insert into the field.
    Returns:
        A confirmation message with the path to the new, filled PDF.
    """
    try:
        doc = fitz.open(pdf_path)
        field_found = False
        for page in doc:
            for field in page.widgets():
                if field.field_name == field_name:
                    field.field_value = value
                    field.update()
                    field_found = True
        
        if not field_found:
            return f"Error: Field '{field_name}' not found in the document."

        # Create a new filename for the filled document
        directory, filename = os.path.split(pdf_path)
        new_filename = f"{os.path.splitext(filename)[0]}_filled.pdf"
        new_path = os.path.join(directory, new_filename)
        
        doc.save(new_path)
        doc.close()
        
        return f"Successfully filled '{field_name}' and saved the updated document to: {new_path}"
    except Exception as e:
        return f"An error occurred while filling the PDF: {str(e)}" 