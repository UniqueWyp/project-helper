import os
import json
from datetime import datetime
from typing import Optional, Callable
from app.tools.git_clone import clone_repo, extract_repo_name
from app.tools.code_analyzer import (
    get_directory_structure,
    read_file_content,
    collect_project_files,
    analyze_tech_stack,
    find_core_modules
)
from app.services.model_service import generate_report, generate_qa_answer

class AnalysisService:
    def __init__(self):
        self.clone_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'repos')
        os.makedirs(self.clone_dir, exist_ok=True)
    
    def analyze_project(self, repo_url: str, progress_callback: Optional[Callable] = None) -> dict:
        if progress_callback:
            progress_callback(step="clone", message="开始克隆仓库...", progress=10)
        
        clone_path = clone_repo(repo_url, self.clone_dir)
        
        if progress_callback:
            progress_callback(step="files", message="收集项目文件信息...", progress=20)
        
        files = collect_project_files(clone_path)
        
        if progress_callback:
            progress_callback(step="structure", message="分析目录结构...", progress=30)
        
        directory_structure = get_directory_structure(clone_path)
        
        if progress_callback:
            progress_callback(step="tech", message="分析技术栈...", progress=40)
        
        tech_stack = analyze_tech_stack(files)
        
        if progress_callback:
            progress_callback(step="core", message="识别核心模块...", progress=50)
        
        core_modules = find_core_modules(files, clone_path)
        
        if progress_callback:
            progress_callback(step="content", message="读取核心文件内容...", progress=60)
        
        core_contents = {}
        for module in core_modules[:10]:
            content = read_file_content(module['path'])
            core_contents[module['path']] = content
        
        if progress_callback:
            progress_callback(step="readme", message="读取项目说明文档...", progress=70)
        
        readme_content = ""
        for name in ['README.md', 'README', 'readme.md', 'readme']:
            readme_path = os.path.join(clone_path, name)
            if os.path.exists(readme_path):
                readme_content = read_file_content(readme_path)
                break
        
        if progress_callback:
            progress_callback(step="generate", message="生成分析报告...", progress=80)
        
        report = generate_report(
            repo_url=repo_url,
            project_name=extract_repo_name(repo_url),
            directory_structure=directory_structure,
            tech_stack=tech_stack,
            core_modules=core_modules,
            core_contents=core_contents,
            readme_content=readme_content,
            files_count=len(files)
        )
        
        if progress_callback:
            progress_callback(step="complete", message="分析完成", progress=100)
        
        return {
            'report': report,
            'clone_path': clone_path,
            'project_name': extract_repo_name(repo_url)
        }
    
    def get_file_content(self, file_path: str) -> str:
        return read_file_content(file_path)
    
    def search_code(self, project_path: str, search_term: str) -> list:
        results = []
        for root, dirs, files in os.walk(project_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    content = read_file_content(filepath)
                    if search_term.lower() in content.lower():
                        results.append({
                            'path': filepath,
                            'content': content[:500] + '...' if len(content) > 500 else content
                        })
                except:
                    continue
        return results[:10]
    
    def answer_question(self, project_path: str, question: str) -> str:
        return generate_qa_answer(project_path, question)
