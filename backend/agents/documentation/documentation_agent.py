import os
import requests
from langsmith import Client

class DocumentationAgent:
    def __init__(self, langsmith_api_key: str, github_token: str):
        self.langsmith_client = Client(api_key=langsmith_api_key)
        self.github_token = github_token

    def log_experiment(self, experiment_data: dict):
        # Log to LangSmith
        self.langsmith_client.create_run(
            name="AVVO Experiment",
            run_type="chain",
            inputs=experiment_data,
            outputs={"status": "logged"}
        )

    def generate_docs(self, system_data: dict) -> str:
        # Generate Markdown documentation
        docs = f"# AVVO System Documentation\n\n## Overview\n{system_data['overview']}\n\n## Agents\n"
        for agent in system_data['agents']:
            docs += f"### {agent['name']}\n{agent['description']}\n\n"
        return docs

    def update_github_pages(self, docs: str):
        # Update GitHub Pages
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("GITHUB_TOKEN not set, skipping GitHub update")
            return
        headers = {"Authorization": f"token {token}"}
        data = {"message": "Update docs", "content": docs.encode('base64')}
        requests.put("https://api.github.com/repos/user/avvo/contents/docs/index.md", headers=headers, json=data)

    def version_control(self, changes: str):
        # Commit changes to Git
        os.system("git add .")
        os.system(f"git commit -m '{changes}'")
        os.system("git push")