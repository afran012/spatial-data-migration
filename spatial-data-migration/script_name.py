import os

def read_gitignore(base_path):
    gitignore_path = os.path.join(base_path, '.gitignore')
    if not os.path.exists(gitignore_path):
        return []
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    ignore_patterns = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return ignore_patterns

def should_ignore(file_path, ignore_patterns):
    for pattern in ignore_patterns:
        if pattern in file_path:
            return True
    return False

def read_file_content(file_path):
    encodings = ['utf-8', 'latin-1', 'iso-8859-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    return f"Error: No se pudo leer el archivo {file_path} con las codificaciones probadas."

def read_project_structure(base_path, output_file, ignore_patterns):
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, base_path)
                if should_ignore(relative_path, ignore_patterns):
                    continue
                f.write(f"### {relative_path}\n")
                file_content = read_file_content(file_path)
                f.write(file_content)
                f.write("\n\n")

base_path = "C:\\Users\\Steev\\Documents\\AiranFranco\\sisc\\athena"
output_file = "project_structure.txt"
ignore_patterns = read_gitignore(base_path)

read_project_structure(base_path, output_file, ignore_patterns)

print(f"Estructura del proyecto generada en {output_file}")