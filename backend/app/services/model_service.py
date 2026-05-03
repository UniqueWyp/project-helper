import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.tools.code_analyzer import read_file_content

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

def get_llm():
    return ChatOpenAI(
        model_name="deepseek-v4-flash",
        openai_api_key=DEEPSEEK_API_KEY,
        openai_api_base=DEEPSEEK_BASE_URL,
        temperature=0.1,
        max_tokens=4096
    )

def generate_report(
    repo_url: str,
    project_name: str,
    directory_structure: str,
    tech_stack: dict,
    core_modules: list,
    core_contents: dict,
    readme_content: str,
    files_count: int
) -> str:
    llm = get_llm()
    
    template = """
你是一个资深的软件架构师和技术文档专家。请根据以下项目信息，生成一份通俗易懂的完整分析报告。

项目信息：
- 仓库地址: {repo_url}
- 项目名称: {project_name}
- 文件总数: {files_count}

技术栈：
- 语言: {languages}
- 框架: {frameworks}
- 工具: {tools}

目录结构：
{directory_structure}

核心模块：
{core_modules_list}

README内容：
{readme_content}

核心文件内容摘要：
{core_contents_summary}

请按照以下结构生成分析报告：

## 一、项目概述
用简单通俗的语言介绍这个项目是做什么的，解决什么问题，有什么特点。

## 二、技术栈分析
详细说明项目使用的编程语言、框架和工具，以及为什么选择这些技术。

## 三、目录结构详解
解释项目的目录组织方式，每个目录的职责是什么。

## 四、核心模块解析
介绍最核心的几个模块/文件，它们的功能和作用。

## 五、设计模式与架构风格
分析项目中使用的设计模式和整体架构风格。

## 六、阅读建议
给初学者提供一个阅读源码的路线图，从哪里开始读比较好。

请务必用简单易懂的语言，避免太多专业术语，让傻子也能看懂！
"""
    
    core_modules_list = "\n".join([f"- {m['path']}" for m in core_modules[:10]])
    core_contents_summary = "\n\n---\n\n".join([
        f"### {path}\n```\n{content[:1000]}\n```" 
        for path, content in list(core_contents.items())[:5]
    ])
    
    prompt = PromptTemplate(
        input_variables=[
            'repo_url', 'project_name', 'files_count',
            'languages', 'frameworks', 'tools',
            'directory_structure', 'core_modules_list',
            'readme_content', 'core_contents_summary'
        ],
        template=template
    )
    
    formatted_prompt = prompt.format(
        repo_url=repo_url,
        project_name=project_name,
        files_count=files_count,
        languages=", ".join(tech_stack.get('languages', [])),
        frameworks=", ".join(tech_stack.get('frameworks', [])),
        tools=", ".join(tech_stack.get('tools', [])),
        directory_structure=directory_structure,
        core_modules_list=core_modules_list,
        readme_content=readme_content[:5000] if readme_content else "无",
        core_contents_summary=core_contents_summary
    )
    
    result = llm.invoke(formatted_prompt)
    return result.content if hasattr(result, 'content') else str(result)

def generate_qa_answer(project_path: str, question: str) -> str:
    llm = get_llm()
    
    files_content = ""
    for root, dirs, filenames in os.walk(project_path):
        for filename in filenames:
            if filename.endswith(('.py', '.js', '.ts', '.md', '.txt', '.java', '.xml', '.yml', '.yaml', '.json', '.sql', '.go', '.rs', '.cpp', '.c', '.h', '.php', '.rb')):
                try:
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, project_path)
                    content = read_file_content(filepath)
                    files_content += f"\n\n---\n\n### {rel_path}\n{content[:2000]}"
                except:
                    continue
        if len(files_content) > 15000:
            break
    
    template = """
你是一个代码分析助手。根据以下项目文件内容，回答用户的问题。

项目文件内容：
{files_content}

用户问题：
{question}

请用简单易懂的语言回答问题，引用相关代码片段来说明。
"""
    
    prompt = template.format(
        files_content=files_content[:15000],
        question=question
    )
    
    result = llm.invoke(prompt)
    return result.content if hasattr(result, 'content') else str(result)
