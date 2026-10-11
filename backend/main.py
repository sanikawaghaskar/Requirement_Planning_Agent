
import os
import logging

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents.requirement_agent import RequirementAnalysisAgent
from agents.planning_agent import ProjectPlanningAgent

app = FastAPI(title="SDLC Requirement and Planning API")

requirement_agent = RequirementAnalysisAgent()
planning_agent = ProjectPlanningAgent()


class ProjectRequest(BaseModel):
    description: str = Field(min_length=10, max_length=10000)


@app.get("/")
def home():
    return {"message": "SDLC Requirement and Planning API is running"}


@app.post("/analyze-and-plan")
def analyze_and_plan(request: ProjectRequest):
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured"
        )

    try:
        requirements = requirement_agent.analyze(
            request.description
        )

        plan = planning_agent.create_plan(requirements)

        return {
            "status": "success",
            "requirements": requirements,
            "plan": plan
        }

    except Exception :
        # Avoid returning API keys or internal error details.
        logger.exception("Analysis or planning failed")
        raise HTTPException(
            status_code=502,
            detail="Analysis or planning failed. Check backend logs."
        )