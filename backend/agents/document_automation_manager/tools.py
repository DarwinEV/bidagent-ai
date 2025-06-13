import os
import json
import re
from google.cloud import documentai
import fitz  # PyMuPDF

# Add project root to sys.path to allow absolute imports from /backend
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.config import load_config
from backend.agents.shared_libraries.utils import get_absolute_path, get_output_path

# ============================================
# Primary Document Analysis Tools
# ============================================

def analyze_document_with_docai(file_path: str, mime_type: str) -> str:
    """Processes a document using the Google Cloud Document AI Form Parser."""
    try:
        config = load_config()
        DOCAI_PROJECT_ID, DOCAI_LOCATION, DOCAI_PROCESSOR_ID = (
            config.get('DOCAI_PROJECT_ID'), config.get('DOCAI_LOCATION'), config.get('DOCAI_PROCESSOR_ID')
        )
        if not all([DOCAI_PROJECT_ID, DOCAI_LOCATION, DOCAI_PROCESSOR_ID]):
            return '{"error": "Document AI Form Parser environment variables are not configured."}'

        absolute_file_path = get_absolute_path(file_path)
        opts = {"api_endpoint": f"{DOCAI_LOCATION}-documentai.googleapis.com"}
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        name = client.processor_path(DOCAI_PROJECT_ID, DOCAI_LOCATION, DOCAI_PROCESSOR_ID)

        with open(absolute_file_path, "rb") as image:
            image_content = image.read()

        raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        
        # Extract relevant data... (This can be enhanced later)
        return documentai.Document.to_json(result.document)

    except Exception as e:
        return f'{{"error": "An error occurred in the Document AI tool: {type(e).__name__} - {str(e)}"}}'

def run_ocr_and_extract_fields(file_path: str, mime_type: str) -> str:
    """
    Runs the full OCR pipeline: calls Google Document AI, processes the raw
    result, and returns a clean JSON blueprint of identified form fields.
    This avoids passing massive raw data back to the agent.
    """
    try:
        config = load_config()
        DOCAI_PROJECT_ID, DOCAI_LOCATION, DOCAI_OCR_PROCESSOR_ID = (
            config.get('DOCAI_PROJECT_ID'), config.get('DOCAI_LOCATION'), config.get('DOCAI_OCR_PROCESSOR_ID')
        )
        if not all([DOCAI_PROJECT_ID, DOCAI_LOCATION, DOCAI_OCR_PROCESSOR_ID]):
            return '{"error": "Document AI OCR environment variables are not configured."}'

        absolute_file_path = get_absolute_path(file_path)
        opts = {"api_endpoint": f"{DOCAI_LOCATION}-documentai.googleapis.com"}
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        name = client.processor_path(DOCAI_PROJECT_ID, DOCAI_LOCATION, DOCAI_OCR_PROCESSOR_ID)

        with open(absolute_file_path, "rb") as image:
            image_content = image.read()

        raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        document = result.document

        words = []
        for page in document.pages:
            for token in page.tokens:
                text_anchor = token.layout.text_anchor
                content = document.text[text_anchor.text_segments[0].start_index : text_anchor.text_segments[0].end_index]
                vertices = token.layout.bounding_poly.normalized_vertices
                words.append({"text": content, "page_number": page.page_number, "coordinates": [{"x": v.x, "y": v.y} for v in vertices]})
        
        form_fields = []
        for i, word in enumerate(words):
            text = word.get("text", "").strip()
            if text.endswith(':'):
                field_name = text[:-1]
                if "signature" in field_name.lower(): continue
                label_coords = word.get("coordinates", [])
                if not label_coords: continue
                
                y0 = min(v['y'] for v in label_coords)
                y1 = max(v['y'] for v in label_coords)
                x1_label = max(v['x'] for v in label_coords)
                
                x0_field, x1_field = x1_label + 0.01, x1_label + 0.3
                
                form_fields.append({
                    "field_name": field_name, "field_type": "text", "is_required": False,
                    "page_number": word.get("page_number", 1),
                    "coordinates": [{"x": x0_field, "y": y0}, {"x": x1_field, "y": y0}, {"x": x1_field, "y": y1}, {"x": x0_field, "y": y1}]
                })

        return json.dumps({"form_fields": form_fields}, indent=2)

    except Exception as e:
        return f'{{"error": "An error occurred during the OCR pipeline: {type(e).__name__} - {str(e)}"}}'

def extract_fields_with_local_heuristics(file_path: str) -> str:
    """
    Analyzes a PDF locally using an aggressive, multi-strategy heuristic approach
    to find all potential form fields. This is the primary, fastest analysis method.
    """
    try:
        doc = fitz.open(get_absolute_path(file_path))
        form_fields = []
        found_field_coords = [] # To avoid re-processing the same field space

        for page_num, page in enumerate(doc):
            # Extract text blocks for better contextual grouping
            blocks = page.get_text("blocks")
            words = page.get_text("words")

            # Strategy: Find ALL underline sections first, then find their context
            underline_fields = [w for w in words if all(c == '_' for c in w[4]) and len(w[4]) > 3]

            for u_field in underline_fields:
                ux0, uy0, ux1, uy1 = u_field[:4]
                field_rect = fitz.Rect(u_field[:4])
                
                # Avoid processing a field that's part of an already found larger field
                if any(field_rect in f for f in found_field_coords):
                    continue

                # Define a "context area" to the left and slightly above the underline
                context_rect = fitz.Rect(0, uy0 - 40, ux0 - 5, uy1 + 5)
                
                context_words = [w for w in words if fitz.Rect(w[:4]).intersects(context_rect)]
                
                field_name = " ".join(w[4] for w in context_words).strip()
                
                # If no direct context, look at the last block of text before the field
                if not field_name:
                    potential_blocks = [b for b in blocks if b[3] < uy0]
                    if potential_blocks:
                        last_block = potential_blocks[-1][4]
                        # Take the last sentence of the last block
                        field_name = last_block.replace('\n', ' ').strip().split('.')[-1].strip()

                if not field_name:
                    field_name = f"Unnamed Field {page_num+1}-{int(ux0)}"

                # Clean and add the field
                field_name = field_name.strip(": ")
                if "signature" in field_name.lower(): continue

                form_fields.append({
                    "field_name": field_name, "field_type": "text", "is_required": False,
                    "page_number": page_num + 1,
                    "coordinates": [
                        {"x": ux0 / page.rect.width, "y": uy0 / page.rect.height},
                        {"x": ux1 / page.rect.width, "y": uy0 / page.rect.height},
                        {"x": ux1 / page.rect.width, "y": uy1 / page.rect.height},
                        {"x": ux0 / page.rect.width, "y": uy1 / page.rect.height}
                    ]
                })
                found_field_coords.append(field_rect)
        
        if not form_fields:
            return '{"error": "No fields were found using local heuristics."}'
            
        # Post-process to merge field names
        merged_fields = {}
        for field in form_fields:
            name = field["field_name"]
            if name in merged_fields:
                # If a field with this name already exists, maybe just keep the first one
                # Or implement a merging logic, for now, we skip
                continue
            else:
                merged_fields[name] = field
        
        return json.dumps({"form_fields": list(merged_fields.values())}, indent=2)

    except Exception as e:
        return f'{{"error": "An error occurred during local heuristic extraction: {type(e).__name__} - {str(e)}"}}'

# ============================================
# PDF Manipulation & Blueprint Tools
# ============================================

def list_pdf_form_fields(pdf_path: str) -> list[str]:
    """Inspects a PDF file and returns a list of its fillable form field names."""
    try:
        doc = fitz.open(get_absolute_path(pdf_path))
        fields = [field.field_name for page in doc for field in page.widgets() if field.field_name]
        return fields if fields else ["No fillable form fields were found in this document."]
    except Exception as e:
        return [f"An error occurred while processing the PDF: {str(e)}"]

def create_fields_from_blueprint(pdf_path: str, json_blueprint_path: str) -> str:
    """Adds empty form fields to a PDF based on a JSON blueprint."""
    try:
        absolute_pdf_path = get_absolute_path(pdf_path)
        with open(get_absolute_path(json_blueprint_path), 'r') as f:
            blueprint = json.load(f)

        doc = fitz.open(absolute_pdf_path)
        for field in blueprint.get("form_fields", []):
            page = doc[field.get("page_number", 1) - 1]
            coords = field.get("coordinates", [])
            if not coords: continue
            
            rect = fitz.Rect(
                coords[0]['x'] * page.rect.width, coords[0]['y'] * page.rect.height,
                coords[2]['x'] * page.rect.width, coords[2]['y'] * page.rect.height
            )

            widget = fitz.Widget()
            widget.rect = rect
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_name = field.get("field_name")
            widget.field_value = "" # Empty for blueprint creation
            widget.field_flags = fitz.PDF_FIELD_IS_REQUIRED # Optional: make fields required
            page.add_widget(widget)
        
        output_path = get_output_path(pdf_path, "_fields_created")
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        return f"Successfully created PDF with empty fields at: {output_path}"
    except Exception as e:
        return f"An error occurred: {type(e).__name__} - {str(e)}"

def fill_form_fields(pdf_path: str, user_data_json: str) -> str:
    """Fills the existing form fields of a PDF with user data."""
    try:
        user_data = json.loads(user_data_json)
        doc = fitz.open(get_absolute_path(pdf_path))
        for page in doc:
            for field in page.widgets():
                if field.field_name in user_data:
                    field.field_value = str(user_data[field.field_name])
                    field.update()
        
        output_path = get_output_path(pdf_path, "_filled", clean_base_name=True)
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        return f"Successfully filled PDF saved at: {output_path}"
    except Exception as e:
        return f"An error occurred: {type(e).__name__} - {str(e)}"

# ============================================
# Utility & Debugging Tools
# ============================================

def save_json_to_file(json_data: str, output_filename: str) -> str:
    """Saves a JSON string to a file and returns the absolute path."""
    try:
        # Use the utility to get a clean path, specifying a 'json' extension
        output_path = get_output_path(output_filename, "", new_extension='json')
        with open(output_path, 'w') as f:
            json.dump(json.loads(json_data), f, indent=2)
        return output_path
    except Exception as e:
        return f"Failed to save file: {str(e)}"

def check_configuration() -> str:
    """Checks and returns the loaded configuration for Document AI."""
    try:
        config = load_config()
        return json.dumps({k: config.get(k, 'Not Set') for k in [
            'DOCAI_PROJECT_ID', 'DOCAI_LOCATION', 'DOCAI_PROCESSOR_ID', 'DOCAI_OCR_PROCESSOR_ID'
        ]}, indent=2)
    except Exception as e:
        return f"An error occurred while checking configuration: {str(e)}" 