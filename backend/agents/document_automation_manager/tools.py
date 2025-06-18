import os
import json
import re
from google.cloud import documentai
import fitz  # PyMuPDF
import numpy as np
import cv2

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
    """
    Processes a document using the Google Cloud Document AI Form Parser and
    returns a clean JSON blueprint of identified form fields.
    """
    def _get_text(text_anchor: documentai.Document.TextAnchor, text: str) -> str:
        """Helper function to extract text from a Document AI TextAnchor."""
        if not text_anchor or not text_anchor.text_segments:
            return ""
        return "".join(
            text[segment.start_index : segment.end_index]
            for segment in text_anchor.text_segments
        ).strip()

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
        document = result.document
        
        form_fields = []
        for page in document.pages:
            for field in page.form_fields:
                field_name = _get_text(field.field_name.text_anchor, document.text)
                # The value bounding box is the actual location of the fillable field.
                vertices = field.field_value.bounding_poly.normalized_vertices
                
                if not field_name or not vertices:
                    continue # Skip fields without a name or location

                # Clean up the field name
                field_name = field_name.replace(":", "").strip()
                if "signature" in field_name.lower():
                    continue

                form_fields.append({
                    "field_name": field_name,
                    "field_type": "text", # Assume text, can be refined if DocAI provides types
                    "is_required": False, # DocAI form parser doesn't reliably provide this
                    "page_number": page.page_number,
                    "coordinates": [{"x": v.x, "y": v.y} for v in vertices]
                })
        
        if not form_fields:
            return '{"error": "Google Document AI did not find any form fields."}'

        return json.dumps({"form_fields": form_fields}, indent=2)

    except Exception as e:
        return f'{{"error": "An error occurred in the Document AI tool: {type(e).__name__} - {str(e)}"}}'

def run_ocr_and_extract_fields(file_path: str, mime_type: str) -> str:
    """
    Runs a hybrid OCR pipeline: calls Google Document AI for OCR, then uses
    local heuristics on the OCR output to find underscore-based form fields.
    This is the most robust method for documents without structured form data.
    """
    def _get_text_from_anchor(anchor, text):
        if not anchor.text_segments:
            return ""
        return "".join(text[s.start_index:s.end_index] for s in anchor.text_segments)

    def _get_bounds_from_token(token):
        # Helper to get a simple (x0, y0, x1, y1) bounding box from vertices
        xs = [v.x for v in token.layout.bounding_poly.normalized_vertices]
        ys = [v.y for v in token.layout.bounding_poly.normalized_vertices]
        return (min(xs), min(ys), max(xs), max(ys))

    def _rects_intersect(r1, r2):
        return not (r1[2] < r2[0] or r1[0] > r2[2] or r1[3] < r2[1] or r1[1] > r2[3])

    def _merge_rects(r1, r2):
        return (min(r1[0], r2[0]), min(r1[1], r2[1]), max(r1[2], r2[2]), max(r1[3], r2[3]))

    try:
        config = load_config()
        # Ensure we are using the OCR processor for this, not the form parser
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

        all_tokens = []
        for page_num, page in enumerate(document.pages):
            for token in page.tokens:
                all_tokens.append({
                    "text": _get_text_from_anchor(token.layout.text_anchor, document.text),
                    "page_number": page_num + 1,
                    "bounds": _get_bounds_from_token(token)
                })

        # Strategy 1: Find all tokens that contain any underscores.
        underline_tokens = [t for t in all_tokens if '_' in t['text']]
        if not underline_tokens:
            return '{"error": "The OCR found no underscore characters to create fields from."}'
            
        # Strategy 2: Merge adjacent underscore tokens into field rectangles.
        merged_underline_rects = []
        sorted_tokens = sorted(underline_tokens, key=lambda t: (t['page_number'], t['bounds'][1], t['bounds'][0]))
        
        current_rect_data = {
            "bounds": sorted_tokens[0]['bounds'], 
            "page": sorted_tokens[0]['page_number']
        }
        for i in range(1, len(sorted_tokens)):
            token_bounds = sorted_tokens[i]['bounds']
            token_page = sorted_tokens[i]['page_number']
            # Check if tokens are on the same page, same line, and horizontally close.
            if token_page == current_rect_data['page'] and \
               abs(token_bounds[1] - current_rect_data['bounds'][1]) < 0.01 and \
               (token_bounds[0] - current_rect_data['bounds'][2]) < 0.05:
                current_rect_data['bounds'] = _merge_rects(current_rect_data['bounds'], token_bounds)
            else:
                merged_underline_rects.append(current_rect_data)
                current_rect_data = {"bounds": token_bounds, "page": token_page}
        merged_underline_rects.append(current_rect_data)

        # Strategy 3: Find a label for each field.
        form_fields = []
        for field_data in merged_underline_rects:
            field_rect = field_data['bounds']
            page_num = field_data['page']
            ux0, uy0, ux1, uy1 = field_rect

            # Heuristic: Look for a label in a context box to the left and slightly above.
            context_rect = (max(0, ux0 - 0.4), uy0 - 0.02, ux0 - 0.005, uy1 + 0.01)
            context_tokens = [t for t in all_tokens if t['page_number'] == page_num and 
                              '_' not in t['text'] and _rects_intersect(t['bounds'], context_rect)]
            context_tokens.sort(key=lambda t: (t['bounds'][1], t['bounds'][0]))
            
            field_name = " ".join(t['text'] for t in context_tokens).strip(": \n")
            if not field_name:
                field_name = f"Unnamed Field {page_num}-{int(ux0*1000)}"
            
            field_name = re.sub(r'\s*\n\s*', ' ', field_name).strip()
            if "signature" in field_name.lower(): continue

            form_fields.append({
                "field_name": field_name, "field_type": "text", "is_required": False,
                "page_number": page_num,
                "coordinates": [{"x": ux0, "y": uy0}, {"x": ux1, "y": uy0}, {"x": ux1, "y": uy1}, {"x": ux0, "y": uy1}]
            })
        
        final_fields = {f["field_name"]: f for f in form_fields}
        return json.dumps({"form_fields": list(final_fields.values())}, indent=2)

    except Exception as e:
        return f'{{"error": "An error occurred during the OCR pipeline: {type(e).__name__} - {str(e)}"}}'

def merge_overlapping_rects(rects: list, tolerance: int = 5) -> list:
    """
    Merges overlapping or very close rectangles into larger bounding boxes.
    This version is corrected to work with fitz.Rect objects.
    """
    if not rects:
        return []
    
    # Sort by top-left corner
    sorted_rects = sorted(rects, key=lambda r: (r.y0, r.x0))
    
    merged = []
    if not sorted_rects:
        return merged

    current_merge_rect = sorted_rects[0]

    for i in range(1, len(sorted_rects)):
        next_rect = sorted_rects[i]
        
        # Create an expanded version of the current rectangle to check for closeness.
        # A new variable is used to avoid modifying the rectangle in the list.
        expanded_rect = fitz.Rect(current_merge_rect)
        expanded_rect.x0 -= tolerance
        expanded_rect.y0 -= tolerance
        expanded_rect.x1 += tolerance
        expanded_rect.y1 += tolerance

        # If they intersect or are very close (the expanded rect intersects), merge them.
        if expanded_rect.intersects(next_rect):
            current_merge_rect.include_rect(next_rect)
        else:
            # If no intersection, the current merge is complete
            merged.append(current_merge_rect)
            current_merge_rect = next_rect
    
    # Add the last merged rectangle
    merged.append(current_merge_rect)
    return merged

def extract_fields_with_local_heuristics(file_path: str) -> str:
    """
    Analyzes a PDF using a high-speed, hybrid approach. It uses computer vision
    to detect lines from the document's vector graphics and combines this with a
    fast text-based search for underscores. This method is optimized for speed
    and is designed to run efficiently on CPU-bound environments.
    """
    try:
        doc = fitz.open(get_absolute_path(file_path))
        all_form_fields = []
        DPI = 300  # Higher DPI for better CV accuracy
        print(f"[DEBUG-VISION] Document '{os.path.basename(file_path)}' has {len(doc)} pages.")

        for page_num, page in enumerate(doc):
            print(f"--- [DEBUG-VISION] Processing Page {page_num + 1}/{len(doc)} ---")
            
            # --- OPTIMIZATION: Early exit for empty or irrelevant pages ---
            if len(page.get_text()) < 50 and not page.get_images():
                print(f"[DEBUG-VISION] Page {page_num + 1} is sparse, skipping.")
                continue

            # --- STRATEGY 1: High-Speed Computer Vision Line Detection ---
            pix = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY, alpha=False)
            img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
            inverted_img = cv2.bitwise_not(img_data)
            
            # --- OPTIMIZATION: Stricter, more refined Hough Line parameters ---
            # Threshold is higher, minLineLength is longer (at least 1 inch at 300 DPI)
            lines = cv2.HoughLinesP(
                inverted_img, rho=1, theta=np.pi / 180, threshold=150,
                minLineLength=300, maxLineGap=20
            )
            
            page_line_rects = []
            if lines is not None:
                print(f"[DEBUG-VISION] Page {page_num + 1}: Found {len(lines)} total lines via computer vision.")
                horizontal_lines = lines[np.abs(lines[:, 0, 1] - lines[:, 0, 3]) < 20] # Allow slightly more skew
                
                # --- FILTERING: Remove lines that are likely borders ---
                page_width_pixels = pix.w
                final_lines = []
                for line in horizontal_lines:
                    x1, _, x2, _ = line[0]
                    if abs(x2 - x1) < (page_width_pixels * 0.9): # Must be less than 90% of page width
                        final_lines.append(line)
                print(f"[DEBUG-VISION] Page {page_num + 1}: Filtered to {len(final_lines)} horizontal, non-border lines.")

                # --- FILTERING: Remove lines that are part of tables ---
                # Sort lines by their y-coordinate to make comparison easier
                final_lines.sort(key=lambda l: l[0][1])
                isolated_lines = []
                for i, line in enumerate(final_lines):
                    is_part_of_table = False
                    y1 = line[0][1]
                    # Check lines before and after in the sorted list
                    for j in range(max(0, i - 5), min(len(final_lines), i + 6)):
                        if i == j: continue
                        y2 = final_lines[j][0][1]
                        # If another line is vertically very close (less than 1/10th of an inch at 300 DPI)
                        if abs(y1 - y2) < 30:
                            is_part_of_table = True
                            break
                    if not is_part_of_table:
                        isolated_lines.append(line)
                
                print(f"[DEBUG-VISION] Page {page_num + 1}: Filtered to {len(isolated_lines)} isolated lines (table rule).")

                for line in isolated_lines:
                    x1, y1, x2, y2 = line[0]
                    # Convert pixel coordinates back to PDF points
                    pdf_rect = fitz.Rect(x1, y1, x2, y2) / DPI * 72
                    pdf_rect.y0 -= 4  # Expand rect slightly for better text capture
                    pdf_rect.y1 += 4
                    page_line_rects.append(pdf_rect)
            else:
                print(f"[DEBUG-VISION] Page {page_num + 1}: Found 0 lines via computer vision.")

            # --- STRATEGY 2: Underscore-Based Text Search ---
            # Correctly get the fitz.Rect for each word containing underscores
            page_underscore_rects = [
                fitz.Rect(word[:4]) for word in page.get_text("words") if "___" in word[4]
            ]
            print(f"[DEBUG-VISION] Page {page_num + 1}: Found {len(page_underscore_rects)} underscore fields via text search.")

            # --- MERGE & REFINE ---
            all_page_rects = page_line_rects + page_underscore_rects
            merged_rects = merge_overlapping_rects(all_page_rects)
            print(f"[DEBUG-VISION] Page {page_num + 1}: Found {len(merged_rects)} total potential fields after merging.")

            page_fields = []
            for rect in merged_rects:
                # Find text to the left of the rectangle to use as a label
                label_rect = fitz.Rect(rect.x0 - 200, rect.y0 - 5, rect.x0 - 5, rect.y1 + 5)
                words = [w[4] for w in page.get_text("words", clip=label_rect)]
                field_name = " ".join(words).strip(": \n")
                if not field_name:
                    field_name = f"Unnamed Field {page_num + 1}-{int(rect.x0)}"
                
                field_name = re.sub(r'\s*\n\s*', ' ', field_name).strip()
                if "signature" in field_name.lower():
                    continue

                page_fields.append({
                    "field_name": field_name,
                    "field_type": "text",
                    "is_required": False,
                    "page_number": page_num + 1,
                    "coordinates": [
                        {"x": rect.x0 / page.rect.width, "y": rect.y0 / page.rect.height},
                        {"x": rect.x1 / page.rect.width, "y": rect.y0 / page.rect.height},
                        {"x": rect.x1 / page.rect.width, "y": rect.y1 / page.rect.height},
                        {"x": rect.x0 / page.rect.width, "y": rect.y1 / page.rect.height},
                    ]
                })
            
            if page_fields:
                all_form_fields.extend(page_fields)

        print(f"--- [DEBUG-VISION] ANALYSIS COMPLETE: Found {len(all_form_fields)} total fields in document. ---")
        
        if not all_form_fields:
            return '{"error": "No form fields were found using local heuristics."}'

        # Remove duplicate fields by name, keeping the first one found.
        final_fields = {f["field_name"]: f for f in reversed(all_form_fields)}.values()
        return json.dumps({"form_fields": list(final_fields)}, indent=2)

    except Exception as e:
        error_message = f'{{"error": "An error occurred in local heuristics: {type(e).__name__} - {str(e)}"}}'
        print(f"[DEBUG-VISION] Exception during analysis: {error_message}")
        return error_message

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