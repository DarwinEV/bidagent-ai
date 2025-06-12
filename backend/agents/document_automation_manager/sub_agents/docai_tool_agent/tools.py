import sys
import os
import json
from google.cloud import documentai

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def analyze_document_with_docai(file_path: str, mime_type: str) -> str:
    """
    Processes a document using the Google Cloud Document AI Form Parser.
    """
    try:
        from backend.config import load_config
        config = load_config()
        DOCAI_PROJECT_ID = config.get('DOCAI_PROJECT_ID')
        DOCAI_LOCATION = config.get('DOCAI_LOCATION')
        DOCAI_PROCESSOR_ID = config.get('DOCAI_PROCESSOR_ID')

        absolute_file_path = os.path.join(PROJECT_ROOT, file_path)

        if not all([DOCAI_PROJECT_ID, DOCAI_LOCATION, DOCAI_PROCESSOR_ID]):
            return '{"error": "Document AI Form Parser environment variables are not configured."}'

        opts = {"api_endpoint": f"{DOCAI_LOCATION}-documentai.googleapis.com"}
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        name = client.processor_path(DOCAI_PROJECT_ID, DOCAI_LOCATION, DOCAI_PROCESSOR_ID)

        with open(absolute_file_path, "rb") as image:
            image_content = image.read()

        raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        document = result.document
        
        output_data = {
            "text": document.text,
            "entities": [{"type": entity.type_, "mention_text": entity.mention_text} for entity in document.entities],
            "key_value_pairs": [
                {
                    "key": field.field_name.text_anchor.content if field.field_name and field.field_name.text_anchor else "",
                    "value": field.field_value.text_anchor.content if field.field_value and field.field_value.text_anchor else ""
                }
                for field in document.form_fields
            ]
        }
        
        return json.dumps(output_data, indent=2)

    except Exception as e:
        return f'{{"error": "An error occurred in the Document AI tool: {type(e).__name__} - {str(e)}"}}' 