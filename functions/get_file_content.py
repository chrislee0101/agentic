import os

MAX_CHARS = 10000

def get_file_content(working_directory, file_path):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        
        # Ensure target file path is within the working directory
        if os.path.commonpath([working_dir_abs, target_file]) != working_dir_abs:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        # Ensure that the file path is a file and not a directory
        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file "{file_path}"'
        
        # Read file with truncation
        with open(target_file, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read(MAX_CHARS)
            
            # Check if the file was truncated
            if file.read(1):
                content += f'[...File "{file_path}" truncated after {MAX_CHARS} characters]'
            
        return content
    
    except Exception as e:
        return f'Error reading file "{file_path}": {str(e)}'
