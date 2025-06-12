import fitz  # PyMuPDF
import json
import os

def fill_pdf_from_blueprint(pdf_path: str, json_blueprint_path: str, user_data_json: str) -> str:
    """
    Fills a PDF form based on a JSON blueprint containing field coordinates and user-provided data.
    Args:
        pdf_path: The relative path to the original PDF document.
        json_blueprint_path: The relative path to the JSON blueprint file.
        user_data_json: A JSON string mapping field names to the data that should be entered.
    Returns:
        A confirmation message with the path to the newly created filled PDF.
    """
    try:
        # Construct absolute paths
        # Assumes the root is the 'backend' directory's parent
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
        absolute_pdf_path = os.path.join(project_root, pdf_path)
        absolute_blueprint_path = os.path.join(project_root, json_blueprint_path)

        # Load the blueprint and user data
        with open(absolute_blueprint_path, 'r') as f:
            blueprint = json.load(f)
        user_data = json.loads(user_data_json)

        # Open the original PDF
        doc = fitz.open(absolute_pdf_path)

        for field in blueprint.get("form_fields", []):
            field_name = field.get("field_name")
            if field_name in user_data:
                page_num = field.get("page_number", 1) - 1 # PyMuPDF is 0-indexed
                page = doc[page_num]
                
                # Get coordinates and create the widget rectangle
                coords = field.get("coordinates")
                if not coords or len(coords) < 2:
                    continue # Skip if coordinates are not valid
                
                # We assume the coordinates define a rectangle
                x0, y0 = coords[0]['x'] * page.rect.width, coords[0]['y'] * page.rect.height
                x1, y1 = coords[1]['x'] * page.rect.width, coords[2]['y'] * page.rect.height
                rect = fitz.Rect(x0, y0, x1, y1)

                # Create a text widget (form field)
                widget = fitz.TextWidget(rect, name=field_name, value=user_data[field_name])
                widget.update()
                page.add_widget(widget)

        # Save the result to a new file in the output directory
        output_dir = os.path.join(project_root, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        original_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"{original_filename}_filled.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        doc.save(output_path)
        doc.close()

        return f"Successfully created filled PDF: {output_path}"

    except Exception as e:
        return f"An error occurred while filling the PDF: {type(e).__name__} - {str(e)}"

def create_fields_from_blueprint(pdf_path: str, json_blueprint_path: str) -> str:
    """
    Adds empty form fields to a PDF based on a JSON blueprint.
    Args:
        pdf_path: The relative path to the original PDF document.
        json_blueprint_path: The relative path to the JSON blueprint file.
    Returns:
        A confirmation message with the path to the new PDF with empty fields.
    """
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
        absolute_pdf_path = os.path.join(project_root, pdf_path)
        absolute_blueprint_path = os.path.join(project_root, json_blueprint_path)

        with open(absolute_blueprint_path, 'r') as f:
            blueprint = json.load(f)

        doc = fitz.open(absolute_pdf_path)

        for field in blueprint.get("form_fields", []):
            page_num = field.get("page_number", 1) - 1
            if page_num >= len(doc): continue
            page = doc[page_num]
            
            coords = field.get("coordinates")
            if not coords or len(coords) < 4: continue

            # Use all four vertices to define the widget rectangle accurately
            rect = fitz.Quad(
                fitz.Point(coords[0]['x'] * page.rect.width, coords[0]['y'] * page.rect.height),
                fitz.Point(coords[1]['x'] * page.rect.width, coords[1]['y'] * page.rect.height),
                fitz.Point(coords[2]['x'] * page.rect.width, coords[2]['y'] * page.rect.height),
                fitz.Point(coords[3]['x'] * page.rect.width, coords[3]['y'] * page.rect.height)
            ).rect

            widget = fitz.TextWidget(rect, name=field.get("field_name"))
            page.add_widget(widget)

        output_dir = os.path.join(project_root, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        original_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"{original_filename}_fields_created.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

        return f"Successfully created PDF with empty form fields at: {output_path}"

    except Exception as e:
        return f"An error occurred while creating PDF fields: {type(e).__name__} - {str(e)}"

def fill_form_fields(pdf_path: str, user_data_json: str) -> str:
    """
    Fills the existing form fields of a PDF with user data.
    Args:
        pdf_path: The relative path to the PDF document that already has form fields.
        user_data_json: A JSON string mapping field names to the data that should be entered.
    Returns:
        A confirmation message with the path to the newly created filled PDF.
    """
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
        absolute_pdf_path = os.path.join(project_root, pdf_path)
        
        user_data = json.loads(user_data_json)
        doc = fitz.open(absolute_pdf_path)

        for page in doc:
            for field in page.widgets():
                if field.field_name in user_data:
                    field.field_value = user_data[field.field_name]
                    field.update()
        
        output_dir = os.path.join(project_root, "output")
        original_filename = os.path.splitext(os.path.basename(pdf_path))[0].replace('_fields_created', '')
        output_filename = f"{original_filename}_filled.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

        return f"Successfully filled PDF saved at: {output_path}"

    except Exception as e:
        return f"An error occurred while filling PDF fields: {type(e).__name__} - {str(e)}" 