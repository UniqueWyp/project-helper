import os
import json
from pathlib import Path

IGNORED_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv', '.idea', '.vscode',
    'dist', 'build', 'target', 'coverage', '.tox', '*.egg-info'
}

IGNORED_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd', '.egg', '.egg-info', '.so', '.dll', '.exe',
    '.zip', '.tar', '.gz', '.rar', '.7z', '.log', '.db', '.sqlite'
}

def should_ignore(path: Path) -> bool:
    parts = path.parts
    for part in parts:
        if part in IGNORED_DIRS:
            return True
    if path.suffix in IGNORED_EXTENSIONS:
        return True
    return False

def get_directory_structure(path: str, prefix: str = "") -> str:
    lines = []
    path_obj = Path(path)
    
    try:
        entries = sorted(path_obj.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return ""
    
    for i, entry in enumerate(entries):
        if should_ignore(entry):
            continue
        
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        
        lines.append(f"{prefix}{connector}{entry.name}")
        
        if entry.is_dir():
            new_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(get_directory_structure(str(entry), new_prefix))
    
    return "\n".join(lines)

def read_file_content(file_path: str, max_size: int = 5242880) -> str:
    try:
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return f"File too large ({file_size} bytes)"
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_file_info(file_path: str) -> dict:
    path_obj = Path(file_path)
    return {
        'path': str(path_obj),
        'name': path_obj.name,
        'size': os.path.getsize(file_path),
        'extension': path_obj.suffix
    }

def collect_project_files(project_path: str) -> list:
    files = []
    for root, dirs, filenames in os.walk(project_path):
        dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]
        
        for filename in filenames:
            file_path = Path(root) / filename
            if should_ignore(file_path):
                continue
            
            try:
                files.append(get_file_info(str(file_path)))
            except:
                pass
    
    return files

def analyze_tech_stack(files: list) -> dict:
    tech_stack = {
        'languages': set(),
        'frameworks': set(),
        'tools': set()
    }
    
    for file in files:
        ext = file['extension'].lower()
        name = file['name'].lower()
        
        if ext == '.py':
            tech_stack['languages'].add('Python')
        elif ext in ('.js', '.jsx'):
            tech_stack['languages'].add('JavaScript')
        elif ext in ('.ts', '.tsx'):
            tech_stack['languages'].add('TypeScript')
        elif ext == '.go':
            tech_stack['languages'].add('Go')
        elif ext == '.rs':
            tech_stack['languages'].add('Rust')
        elif ext == '.java':
            tech_stack['languages'].add('Java')
        elif ext == '.cpp' or ext == '.hpp':
            tech_stack['languages'].add('C++')
        elif ext == '.md':
            tech_stack['tools'].add('Markdown')
        
        if 'package.json' in name:
            tech_stack['tools'].add('Node.js')
            tech_stack['tools'].add('npm')
        elif 'yarn.lock' in name:
            tech_stack['tools'].add('Yarn')
        elif 'pnpm-lock.yaml' in name:
            tech_stack['tools'].add('pnpm')
        elif 'requirements.txt' in name:
            tech_stack['tools'].add('pip')
        elif 'pyproject.toml' in name:
            tech_stack['tools'].add('Poetry')
        elif 'go.mod' in name:
            tech_stack['tools'].add('Go Modules')
        elif 'Cargo.toml' in name:
            tech_stack['tools'].add('Cargo')
        
        if 'vue' in name or ext == '.vue':
            tech_stack['frameworks'].add('Vue.js')
        elif 'react' in name or ext in ('.jsx', '.tsx'):
            tech_stack['frameworks'].add('React')
        elif 'angular' in name:
            tech_stack['frameworks'].add('Angular')
        elif 'fastapi' in name:
            tech_stack['frameworks'].add('FastAPI')
        elif 'django' in name:
            tech_stack['frameworks'].add('Django')
    
    return {
        'languages': list(tech_stack['languages']),
        'frameworks': list(tech_stack['frameworks']),
        'tools': list(tech_stack['tools'])
    }

def find_core_modules(files: list, project_path: str) -> list:
    core_patterns = ['main', 'app', 'cli', 'core', 'lib', 'utils', 'src']
    core_modules = []
    
    for file in files:
        rel_path = os.path.relpath(file['path'], project_path)
        parts = rel_path.split(os.sep)
        
        if any(pattern in parts[0].lower() for pattern in core_patterns):
            core_modules.append(file)
    
    return sorted(core_modules, key=lambda x: x['path'])
