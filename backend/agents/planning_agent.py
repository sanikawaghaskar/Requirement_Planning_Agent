
# import json
# import os

# from groq import Groq
# from dotenv import load_dotenv

# load_dotenv()

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# class ProjectPlanningAgent:

#     def create_plan(self, requirements: dict) -> dict:
#         prompt = f"""
# You are an experienced software project planner.

# Create an implementation plan from this requirement specification:
# {json.dumps(requirements, indent=2)}

# Return valid JSON with these keys:
# {{
#   "project_title": "project name",
#   "recommended_stack": {{
#     "frontend": "technology",
#     "backend": "technology",
#     "database": "technology"
#   }},
#   "milestones": [
#     {{
#       "name": "milestone name",
#       "tasks": [
#         {{
#           "id": "T1",
#           "title": "task title",
#           "description": "what to implement",
#           "priority": "High",
#           "depends_on": [],
#           "related_requirements": ["FR1"],
#           "test_plan": ["how to verify the task"]
#         }}
#       ]
#     }}
#   ],
#   "risks": [],
#   "implementation_order": ["T1"]
# }}

# Rules:
# - Keep tasks small, concrete, and implementable.
# - Use task IDs consistently.
# - Dependencies must reference existing task IDs.
# - Map tasks to relevant requirement IDs.
# - Do not claim a task is completed.
# - Keep the plan appropriate for the project's scope.
# - Return JSON only.
# """

#         response = client.chat.completions.create(
#             model="openai/gpt-oss-20b",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are a software development project planner."
#                 },
#                 {"role": "user", "content": prompt}
#             ],
#             response_format={"type": "json_object"},
#             temperature=0.2
#         )

#         content = response.choices[0].message.content
#         return json.loads(content)


import json
import os

from typing import Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def validate_plan(plan: dict, requirements: dict) -> None:
    """Raise ValueError when the generated plan is structurally invalid."""

    if not isinstance(plan, dict):
        raise ValueError("Plan must be a JSON object.")

    milestones = plan.get("milestones")

    if not isinstance(milestones, list) or not milestones:
        raise ValueError("Plan must contain a non-empty milestones list.")

    task_ids = []
    task_dependencies = {}
    covered_requirements = set()

    for milestone in milestones:
        if not isinstance(milestone, dict):
            raise ValueError(
                "Each milestone must be an object, not a string or list."
            )

        if not isinstance(milestone.get("name"), str):
            raise ValueError("Every milestone must have a name.")

        tasks = milestone.get("tasks")

        if not isinstance(tasks, list):
            raise ValueError("Every milestone must contain a tasks list.")

        for task in tasks:
            if not isinstance(task, dict):
                raise ValueError("Every task must be a JSON object.")

            task_id = task.get("id")

            if not isinstance(task_id, str) or not task_id.strip():
                raise ValueError("Every task must have a non-empty ID.")

            if task_id in task_ids:
                raise ValueError(f"Duplicate task ID: {task_id}")

            task_ids.append(task_id)

            dependencies = task.get("depends_on", [])
            if not isinstance(dependencies, list):
                raise ValueError(f"Dependencies for {task_id} must be a list.")

            task_dependencies[task_id] = dependencies

            related = task.get("related_requirements", [])
            if not isinstance(related, list):
                raise ValueError(
                    f"Related requirements for {task_id} must be a list."
                )

            covered_requirements.update(related)

            if not isinstance(task.get("test_plan"), list):
                raise ValueError(f"Task {task_id} must include a test_plan list.")

    known_task_ids = set(task_ids)

    for task_id, dependencies in task_dependencies.items():
        for dependency in dependencies:
            if dependency not in known_task_ids:
                raise ValueError(
                    f"{task_id} depends on unknown task {dependency}."
                )
            if dependency == task_id:
                raise ValueError(f"{task_id} cannot depend on itself.")

    order = plan.get("implementation_order")

    if not isinstance(order, list):
        raise ValueError("implementation_order must be a list.")

    if len(order) != len(set(order)) or set(order) != known_task_ids:
        raise ValueError(
            "implementation_order must contain every task ID exactly once."
        )

    positions = {task_id: i for i, task_id in enumerate(order)}

    for task_id, dependencies in task_dependencies.items():
        for dependency in dependencies:
            if positions[dependency] >= positions[task_id]:
                raise ValueError(
                    f"Dependency {dependency} must appear before {task_id}."
                )

    functional_requirements = {
        item["id"]
        for item in requirements.get("functional_requirements", [])
        if isinstance(item, dict) and "id" in item
    }

    missing = functional_requirements - covered_requirements

    if missing:
        raise ValueError(
            "Uncovered functional requirements: " + ", ".join(sorted(missing))
        )


class ProjectPlanningAgent:

    def create_plan(self, requirements: dict) -> dict:

        prompt = f"""
You are a senior software architect and project planning agent.

Your job is to convert software requirements into a COMPLETE,
IMPLEMENTABLE software development plan.

INPUT REQUIREMENTS:
{json.dumps(requirements, indent=2)}

Return a valid JSON object with this exact structure:

{{
  "project_title": "Project name",

  "recommended_stack": {{
    "frontend": "Technology",
    "backend": "Technology",
    "database": "Technology"
  }},

  "milestones": [
    {{
      "name": "Milestone name",
      "goal": "What this milestone achieves",
      "tasks": [
        {{
          "id": "T1",
          "title": "Short task title",
          "description": "Specific implementation instructions",
          "priority": "High",
          "depends_on": [],
          "related_requirements": ["FR1"],
          "test_plan": [
            "Specific steps to verify the task"
          ]
        }}
      ]
    }}
  ],

  "risks": [
    {{
      "risk": "Description of the risk",
      "impact": "High",
      "mitigation": "How to reduce the risk"
    }}
  ],

  "implementation_order": ["T1"]
}}

MANDATORY PLANNING RULES:

1. REQUIREMENT COVERAGE
- Cover EVERY functional requirement in the input.
- Every functional requirement ID must appear in at least one task's
  related_requirements list.
- Do not invent requirement IDs.
- Include tasks for relevant non-functional requirements.

2. MILESTONES
- Create multiple logical milestones appropriate to the project.
- For a typical small CRUD application, consider:
  project setup, database/backend, authentication, core features,
  frontend integration, testing and release.
- Combine milestones where appropriate for a smaller project.
- Do not return just one milestone with only two tasks when the
  requirements clearly need more implementation work.

3. TASK QUALITY
- Create concrete, small, implementable tasks.
- Each task must have a unique ID: T1, T2, T3, and so on.
- Include a useful description and at least one test_plan item.
- Include implementation and integration tasks where needed.
- Include security tasks relevant to authentication and user data.
- Do not claim that any task has been completed.

4. DEPENDENCIES
- Every depends_on ID must refer to an existing task.
- Do not create circular dependencies.
- A task must not depend on itself.
- Tasks without prerequisites should have an empty depends_on list.

5. IMPLEMENTATION ORDER
- Include every task ID exactly once in implementation_order.
- Put prerequisites before tasks that depend on them.
- Use only IDs that exist in the milestones.

6. HONESTY
- Record unclear details as assumptions or risks when appropriate.
- Do not claim that generated tasks or tests have actually been executed.
- Recommend a consistent technology stack.

Return JSON only. Do not include Markdown or explanations outside JSON.
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise software project planner."
                        "Return only a valid JSON object matching"
                        "the requested structure."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            reasoning_format="hidden",
            reasoning_effort="low",
            max_completion_tokens=8192,
            temperature=1
        )

        content = response.choices[0].message.content

        return json.loads(content)
