import os
import json
import re
import fitz  # PyMuPDF
import numpy as np
import cv2
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

# Add project root to sys.path to allow absolute imports from /backend
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.config import load_config
from backend.agents.shared_libraries.utils import get_absolute_path, get_output_path

# ============================================
# Tier 1 Analysis Tool: Azure OCR
# ============================================

def create_form_field_blueprint_from_azure(file_path: str) -> str:
    """
    (Primary Tool) Analyzes a document using Azure Document Intelligence to find all
    words and their coordinates. It saves the raw analysis to a JSON file for debugging and
    then applies heuristics to identify likely form field labels, creating a JSON "blueprint".
    """
    try:
        config = load_config()
        AZURE_DOC_INTEL_ENDPOINT = config.get('AZURE_DOC_INTEL_ENDPOINT')
        AZURE_DOC_INTEL_KEY = config.get('AZURE_DOC_INTEL_KEY')

        if not AZURE_DOC_INTEL_ENDPOINT or not AZURE_DOC_INTEL_KEY:
            return '{"error": "Azure Document Intelligence credentials are not configured."}'

        absolute_file_path = get_absolute_path(file_path)
        client = DocumentIntelligenceClient(
            endpoint=AZURE_DOC_INTEL_ENDPOINT, credential=AzureKeyCredential(AZURE_DOC_INTEL_KEY)
        )

        with open(absolute_file_path, "rb") as f:
            poller = client.begin_analyze_document(
                "prebuilt-layout", f.read(), content_type="application/octet-stream"
            )
        result = poller.result(timeout=600)
        
        raw_output_path = get_output_path(file_path, "_azure_raw_analysis.json")
        try:
            with open(raw_output_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save raw Azure analysis file: {e}")

        if not result.pages:
            return '{"error": "Azure did not return any pages from the document."}'

        form_fields = []
        for page_num, page in enumerate(result.pages):
            # The rest of this tool is a basic heuristic. The raw output is the most valuable part.
            potential_labels = [w for w in page.words if w.content.strip().endswith(':')]
            for label_word in potential_labels:
                label_text = label_word.content.strip().replace(":", "")
                if "signature" in label_text.lower(): continue
                label_poly = label_word.polygon
                label_x_coords = [label_poly[i] for i in range(0, len(label_poly), 2)]
                label_y_coords = [label_poly[i+1] for i in range(0, len(label_poly), 2)]
                
                field_x0 = max(label_x_coords) + 10
                field_y0 = min(label_y_coords) - 5
                field_x1 = page.width - 50
                field_y1 = max(label_y_coords) + 5

                if field_x1 <= field_x0: continue

                form_fields.append({
                    "field_name": label_text, "field_type": "text", "page_number": page_num + 1,
                    "coordinates": [
                        {"x": field_x0 / page.width, "y": field_y0 / page.height},
                        {"x": field_x1 / page.width, "y": field_y0 / page.height},
                        {"x": field_x1 / page.width, "y": field_y1 / page.height},
                        {"x": field_x0 / page.width, "y": field_y1 / page.height},
                    ]
                })

        if not form_fields:
            return f'{{"error": "The Azure-based heuristic analysis did not identify any potential form fields.", "raw_output_path": "{raw_output_path}"}}'

        return json.dumps({"form_fields": form_fields, "raw_output_path": raw_output_path}, indent=2)

    except Exception as e:
        return f'{{"error": "An error occurred in the Azure blueprint tool: {type(e).__name__} - {str(e)}"}}'

# ============================================
# Tier 2 Analysis Tool: Local CV/Text Heuristics
# ============================================

def merge_overlapping_rects(rects: list, tolerance: int = 5) -> list:
    """ Merges overlapping or very close fitz.Rect objects into larger bounding boxes. """
    if not rects: return []
    sorted_rects = sorted(rects, key=lambda r: (r.y0, r.x0))
    merged = []
    current_merge_rect = sorted_rects[0]
    for i in range(1, len(sorted_rects)):
        next_rect = sorted_rects[i]
        expanded_rect = fitz.Rect(current_merge_rect)
        expanded_rect.x1 += tolerance
        expanded_rect.y1 += tolerance
        if expanded_rect.intersects(next_rect):
            current_merge_rect.include_rect(next_rect)
        else:
            merged.append(current_merge_rect)
            current_merge_rect = next_rect
    merged.append(current_merge_rect)
    return merged

def extract_fields_with_local_heuristics(file_path: str) -> str:
    """
    (Fallback Tool) Analyzes a PDF using a high-speed, hybrid approach. It uses computer
    vision (OpenCV) to detect lines and combines this with a text search for underscores.
    This is the fallback if Azure OCR fails to find fields.
    """
    try:
        doc = fitz.open(get_absolute_path(file_path))
        all_form_fields = []
        DPI = 300
        print(f"[DEBUG-VISION] Document '{os.path.basename(file_path)}' has {len(doc)} pages.")

        for page_num, page in enumerate(doc):
            print(f"--- [DEBUG-VISION] Processing Page {page_num + 1}/{len(doc)} ---")
            
            if len(page.get_text()) < 50 and not page.get_images():
                print(f"[DEBUG-VISION] Page {page_num + 1} is sparse, skipping.")
                continue

            pix = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY, alpha=False)
            img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w)
            inverted_img = cv2.bitwise_not(img_data)
            lines = cv2.HoughLinesP(inverted_img, rho=1, theta=np.pi/180, threshold=150, minLineLength=300, maxLineGap=20)
            
            page_line_rects = []
            if lines is not None:
                print(f"[DEBUG-VISION] Page {page_num + 1}: Found {len(lines)} total lines via computer vision.")
                horizontal_lines = lines[np.abs(lines[:, 0, 1] - lines[:, 0, 3]) < 20]
                
                final_lines = []
                for line in horizontal_lines:
                    if abs(line[0][2] - line[0][0]) < (pix.w * 0.9):
                        final_lines.append(line)
                print(f"[DEBUG-VISION] Page {page_num + 1}: Filtered to {len(final_lines)} horizontal, non-border lines.")

                final_lines.sort(key=lambda l: l[0][1])
                isolated_lines = []
                for i, line in enumerate(final_lines):
                    is_part_of_table = any(abs(line[0][1] - final_lines[j][0][1]) < 30 for j in range(max(0, i-5), min(len(final_lines), i+6)) if i != j)
                    if not is_part_of_table:
                        isolated_lines.append(line)
                print(f"[DEBUG-VISION] Page {page_num + 1}: Filtered to {len(isolated_lines)} isolated lines (table rule).")
                page_line_rects = [(fitz.Rect(line[0][:4]) / DPI * 72) for line in isolated_lines]
            else:
                print(f"[DEBUG-VISION] Page {page_num + 1}: Found 0 lines via computer vision.")

            page_underscore_rects = [fitz.Rect(word[:4]) for word in page.get_text("words") if "___" in word[4]]
            print(f"[DEBUG-VISION] Page {page_num + 1}: Found {len(page_underscore_rects)} underscore fields via text search.")

            all_page_rects = page_line_rects + page_underscore_rects
            merged_rects = merge_overlapping_rects(all_page_rects)
            print(f"[DEBUG-VISION] Page {page_num + 1}: Found {len(merged_rects)} total potential fields after merging.")

            for rect in merged_rects:
                label_rect = fitz.Rect(rect.x0 - 200, rect.y0 - 5, rect.x0 - 5, rect.y1 + 5)
                field_name = " ".join([w[4] for w in page.get_text("words", clip=label_rect)]).strip(": \n")
                if not field_name: field_name = f"Unnamed Field {page_num + 1}-{int(rect.x0)}"
                field_name = re.sub(r'\\s*\\n\\s*', ' ', field_name).strip()
                if "signature" in field_name.lower(): continue

                all_form_fields.append({
                    "field_name": field_name, "field_type": "text", "is_required": False, "page_number": page_num + 1,
                    "coordinates": [
                        {"x": rect.x0/page.rect.width, "y": rect.y0/page.rect.height}, {"x": rect.x1/page.rect.width, "y": rect.y0/page.rect.height},
                        {"x": rect.x1/page.rect.width, "y": rect.y1/page.rect.height}, {"x": rect.x0/page.rect.width, "y": rect.y1/page.rect.height}
                    ]
                })
        
        if not all_form_fields: return '{"error": "No form fields were found using local heuristics."}'
        final_fields = {f["field_name"]: f for f in reversed(all_form_fields)}.values()
        return json.dumps({"form_fields": list(final_fields)}, indent=2)

    except Exception as e:
        error_message = f'{{"error": "An error occurred in local heuristics: {type(e).__name__} - {str(e)}"}}'
        print(f"[DEBUG-VISION] Exception during analysis: {error_message}")
        return error_message

# ============================================
# PDF Manipulation & Blueprint Tools
# ============================================

def list_pdf_form_fields(pdf_path: str) -> str:
    """Inspects a PDF file and returns a JSON list of its fillable form field names."""
    try:
        doc = fitz.open(get_absolute_path(pdf_path))
        fields = [field.field_name for page in doc for field in page.widgets() if field.field_name]
        if not fields:
            return '{"fields": [], "message": "No existing interactive form fields were found."}'
        return json.dumps({"fields": fields, "message": f"Found {len(fields)} existing fields."})
    except Exception as e:
        return f'{{"error": "An error occurred while processing the PDF: {str(e)}"}}'

def create_fields_from_blueprint(pdf_path: str, json_blueprint_path: str) -> str:
    """Adds empty form fields to a PDF based on a JSON blueprint file."""
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
            widget = fitz.Widget(rect=rect, field_type=fitz.PDF_WIDGET_TYPE_TEXT, field_name=field.get("field_name"), field_value="")
            page.add_widget(widget)
        
        output_path = get_output_path(pdf_path, "_fields_created")
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        return f'{{"success": true, "path": "{output_path}"}}'
    except Exception as e:
        return f'{{"error": "An error occurred: {type(e).__name__} - {str(e)}"}}'

def fill_form_fields(pdf_path: str, user_data_json: str) -> str:
    """Fills the existing form fields of a PDF with user data from a JSON string."""
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
        return f'{{"success": true, "path": "{output_path}"}}'
    except Exception as e:
        return f'{{"error": "An error occurred: {type(e).__name__} - {str(e)}"}}'

# ============================================
# Utility & Debugging Tools
# ============================================

def save_json_to_file(json_data: str, output_filename: str) -> str:
    """Saves a JSON string to a file in the output directory."""
    try:
        output_path = get_output_path(output_filename, "", new_extension='json')
        with open(output_path, 'w') as f:
            # First, validate if json_data is a string that can be loaded into a dict
            data_dict = json.loads(json_data)
            json.dump(data_dict, f, indent=2)
        return f'{{"success": true, "path": "{output_path}"}}'
    except json.JSONDecodeError:
        return '{"error": "Input string is not valid JSON."}'
    except Exception as e:
        return f'{{"error": "Failed to save file: {str(e)}"}}'

def check_configuration() -> str:
    """Checks and returns the loaded configuration for Azure Document AI."""
    try:
        config = load_config()
        return json.dumps({k: config.get(k, 'Not Set') for k in [
            'AZURE_DOC_INTEL_ENDPOINT', 'AZURE_DOC_INTEL_KEY'
        ]}, indent=2)
    except Exception as e:
        return f"An error occurred while checking configuration: {str(e)}"

def get_tools():
    """Returns the list of tools for the agent."""
    return [
        list_pdf_form_fields,
        create_form_field_blueprint_from_azure,
        extract_fields_with_local_heuristics,
        save_json_to_file,
        create_fields_from_blueprint,
        fill_form_fields,
        check_configuration,
    ] 