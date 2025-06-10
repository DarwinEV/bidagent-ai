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

def find_text_coordinates(pdf_path: str, text_to_find: str) -> list[dict]:
    """
    Finds all occurrences of a text string in a PDF and returns their coordinates.
    Args:
        pdf_path: The local path to the PDF file.
        text_to_find: The text string to search for.
    Returns:
        A list of dictionaries, each containing the page number and bounding box of an occurrence.
    """
    try:
        doc = fitz.open(pdf_path)
        results = []
        for i, page in enumerate(doc):
            areas = page.search_for(text_to_find)
            for area in areas:
                results.append({
                    "page": i,
                    "x0": area.x0,
                    "y0": area.y0,
                    "x1": area.x1,
                    "y1": area.y1
                })
        doc.close()
        if not results:
            return [{"error": f"Text '{text_to_find}' not found in the document."}]
        return results
    except Exception as e:
        return [{"error": f"An error occurred while searching for text: {str(e)}"}]

def create_and_fill_field(pdf_path: str, page_number: int, field_name: str, x0: float, y0: float, x1: float, y1: float, value: str) -> str:
    """
    Creates a new text field and fills it with a value in a single atomic operation.
    This creates a new output file named '<original>_filled.pdf'.
    Args:
        pdf_path: The local path to the original PDF file.
        page_number: The zero-based index of the page to add the field to.
        field_name: The unique name for the new form field.
        x0, y0, x1, y1: The coordinates defining the bounding box of the new field.
        value: The text value to insert into the field.
    Returns:
        A confirmation message with the path to the new, filled PDF.
    """
    try:
        # Determine the output path. If a filled version already exists, use it as the input.
        directory, filename = os.path.split(pdf_path)
        base_filename, ext = os.path.splitext(filename)
        filled_filename = f"{base_filename}_filled.pdf"
        output_path = os.path.join(directory, filled_filename)

        input_path = output_path if os.path.exists(output_path) else pdf_path
        
        doc = fitz.open(input_path)
        if page_number >= len(doc):
            return f"Error: Page number {page_number} is out of bounds."
        page = doc[page_number]
        
        rect = fitz.Rect(x0, y0, x1, y1)
        widget = fitz.Widget()
        widget.rect = rect
        widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        widget.field_name = field_name
        widget.field_value = value # Set the value directly
        widget.field_flags = fitz.PDF_FIELD_IS_REQUIRED
        
        page.add_widget(widget)
        
        doc.save(output_path)
        doc.close()
        
        return f"Successfully created and filled field '{field_name}' on page {page_number}. Document saved to: {output_path}"
    except Exception as e:
        return f"An error occurred while creating and filling the field: {str(e)}"

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