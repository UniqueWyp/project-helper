import os
import re
import subprocess
import shutil
import sys
from typing import Optional

def extract_repo_name(url: str) -> str:
    patterns = [
        r"https?://github\.com/([^/]+)/([^/]+)(\.git)?$",
        r"git@github\.com:([^/]+)/([^/]+)(\.git)?$"
    ]
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return f"{match.group(1)}_{match.group(2)}"
    return "unknown_repo"

def remove_directory(path: str) -> bool:
    if not os.path.exists(path):
        return True
    
    try:
        if sys.platform == 'win32':
            result = subprocess.run(
                ['powershell', '-Command', f'Remove-Item -Path "{path}" -Recurse -Force'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        else:
            shutil.rmtree(path)
            return True
    except Exception:
        return False

def clone_repo(repo_url: str, target_dir: str, retries: int = 3) -> str:
    repo_name = extract_repo_name(repo_url)
    clone_path = os.path.join(target_dir, repo_name)
    
    if os.path.exists(clone_path):
        if not remove_directory(clone_path):
            raise Exception(f"无法删除已存在的目录: {clone_path}")
    
    os.makedirs(target_dir, exist_ok=True)
    
    for attempt in range(retries):
        try:
            env = os.environ.copy()
            env['GIT_HTTP_MAX_REQUEST_BUFFER'] = '1048576000'
            env['GIT_HTTP_POST_BUFFER'] = '1048576000'
            
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', '--single-branch', repo_url, clone_path],
                env=env,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return clone_path
            else:
                if attempt < retries - 1:
                    remove_directory(clone_path)
                    continue
                else:
                    raise Exception(f"Failed to clone repository: {result.stderr}")
                    
        except subprocess.TimeoutExpired:
            if attempt < retries - 1:
                remove_directory(clone_path)
                continue
            else:
                raise Exception(f"Clone operation timed out after {retries} attempts")
        except Exception as e:
            if attempt < retries - 1:
                remove_directory(clone_path)
                continue
            else:
                raise Exception(f"Clone error: {str(e)}")
    
    raise Exception(f"Failed to clone repository after {retries} attempts")