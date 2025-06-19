import os

def get_absolute_path(relative_or_absolute_path: str) -> str:
    """
    Converts a given path to an absolute path.
    If the path is already absolute, it returns it unchanged.
    If it's relative, it resolves it from the project root.
    """
    if os.path.isabs(relative_or_absolute_path):
        return relative_or_absolute_path
        
    # Assumes this script's location is 'backend/agents/shared_libraries/utils.py'
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    return os.path.join(project_root, relative_or_absolute_path)

def get_output_path(original_path: str, suffix: str, new_extension: str = "pdf", clean_base_name: bool = False) -> str:
    """
    Creates a standardized output path for a processed file.
    Handles different file extensions and can clean the base name.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    output_dir = os.path.join(project_root, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Correctly get the base name without any extensions
    base_name = os.path.basename(original_path)
    # Split on the first dot to handle names like 'file.rev1.pdf'
    true_base_name = base_name.split('.')[0]
    
    if clean_base_name:
        true_base_name = true_base_name.replace('_fields_created', '')

    new_filename = f"{true_base_name}{suffix}.{new_extension}"
    return os.path.join(output_dir, new_filename) 