from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
from agents.trend_discovery.trend_discovery_agent import TrendDiscoveryAgent
from agents.story_ideation.story_ideation_agent import StoryIdeationAgent
from agents.documentation.documentation_agent import DocumentationAgent

router = APIRouter()

class AgentResponse(BaseModel):
    agent: str
    status: str
    message: str

class TrendData(BaseModel):
    platform: str
    summary: str

class ScriptData(BaseModel):
    trend: dict
    script: str
    critique: str
    score: float

trend_agent = TrendDiscoveryAgent(gemini_api_key=os.getenv("GEMINI_API_KEY"))
story_agent = StoryIdeationAgent(gemini_api_key=os.getenv("GEMINI_API_KEY"))
doc_agent = DocumentationAgent(langsmith_api_key=os.getenv("LANGCHAIN_API_KEY"), github_token=os.getenv("GITHUB_TOKEN"))

@router.get("/", response_model=List[AgentResponse])
async def get_agents():
    # Placeholder for agent statuses
    return [
        {"agent": "Trend Discovery", "status": "Active", "message": "Scanning trends"},
        {"agent": "Story Ideation", "status": "Idle", "message": "Ready for input"},
        {"agent": "Video Generation", "status": "Idle", "message": "Ready to generate"},
        {"agent": "Optimization & Feedback", "status": "Active", "message": "Analyzing data"},
        {"agent": "Publisher", "status": "Idle", "message": "Ready to publish"},
        {"agent": "Documentation", "status": "Active", "message": "Logging activities"}
    ]

@router.post("/trigger/{agent_name}")
async def trigger_agent(agent_name: str):
    if agent_name == "trend_discovery":
        trends = await trend_agent.discover_trends()
        return {"trends": trends}
    elif agent_name == "story_ideation":
        trends = await trend_agent.discover_trends()
        scripts = story_agent.generate_scripts(trends)
        ranked_scripts = story_agent.rank_scripts(scripts)
        return {"scripts": ranked_scripts}
    elif agent_name == "video_generation":
        # Trigger Node.js video generation server
        import subprocess
        subprocess.run(["node", "agents/video_generation/index.js"], cwd="..")
        return {"message": "Video generation started"}
    elif agent_name == "publisher":
        # Trigger Node.js publisher server
        import subprocess
        subprocess.run(["node", "agents/publisher/index.js"], cwd="..")
        return {"message": "Publishing started"}
    elif agent_name == "documentation":
        system_data = {"overview": "AVVO System", "agents": [{"name": "Trend Discovery", "description": "Scans trends"}]}
        docs = doc_agent.generate_docs(system_data)
        doc_agent.update_github_pages(docs)
        doc_agent.version_control("Updated documentation")
        return {"message": "Documentation updated"}
    if agent_name not in ["trend_discovery", "story_ideation", "video_generation", "optimization_feedback", "publisher", "documentation"]:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": f"Triggered {agent_name} agent"}

@router.get("/trends", response_model=List[TrendData])
async def get_trends():
    trends = await trend_agent.discover_trends()
    return trends

@router.get("/scripts", response_model=List[ScriptData])
async def get_scripts():
    trends = await trend_agent.discover_trends()
    scripts = story_agent.generate_scripts(trends)
    ranked_scripts = story_agent.rank_scripts(scripts)
    return ranked_scripts