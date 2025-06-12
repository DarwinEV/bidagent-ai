import os
import json

def save_json_to_file(json_data: str, output_filename: str) -> str:
    """
    Saves a JSON string to a file in the 'output' directory.
    """
    try:
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_path = os.path.join(output_dir, output_filename)
        
        data_dict = json.loads(json_data)
        
        with open(file_path, 'w') as f:
            json.dump(data_dict, f, indent=2)
            
        return f"Successfully saved blueprint to {file_path}"
        
    except Exception as e:
        return f"Failed to save file: {str(e)}" 