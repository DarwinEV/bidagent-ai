import sys
import os
import json
from google.cloud import documentai

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def get_document_text_with_coordinates(file_path: str, mime_type: str) -> str:
    """
    Processes a document using the Google Cloud Document AI OCR processor
    to extract all words and their coordinates.
    """
    try:
        from backend.config import load_config
        config = load_config()
        DOCAI_PROJECT_ID = config.get('DOCAI_PROJECT_ID')
        DOCAI_LOCATION = config.get('DOCAI_LOCATION')
        DOCAI_OCR_PROCESSOR_ID = config.get('DOCAI_OCR_PROCESSOR_ID')

        absolute_file_path = os.path.join(PROJECT_ROOT, file_path)

        if not all([DOCAI_PROJECT_ID, DOCAI_LOCATION, DOCAI_OCR_PROCESSOR_ID]):
            return '{"error": "Document AI OCR environment variables are not configured."}'

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
                text = token.layout.text_anchor.text_segments[0]
                start_index = text.start_index
                end_index = text.end_index
                word_text = document.text[start_index:end_index]
                vertices = token.layout.bounding_poly.normalized_vertices
                words.append({
                    "text": word_text,
                    "page_number": page.page_number,
                    "coordinates": [{"x": v.x, "y": v.y} for v in vertices]
                })
        
        return json.dumps({"words": words}, indent=2)

    except Exception as e:
        return f'{{"error": "An error occurred in the OCR tool: {type(e).__name__} - {str(e)}"}}' 