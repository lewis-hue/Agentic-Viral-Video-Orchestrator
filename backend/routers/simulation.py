from fastapi import APIRouter
from agents.simulation.simulation_agent import SimulationAgent

router = APIRouter()

sim_agent = SimulationAgent()

@router.get("/run")
async def run_simulation():
    results = sim_agent.run_simulation()
    return results