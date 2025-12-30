from langgraph.graph import StateGraph, END
from app.agents.workflow_state import WorkflowState

from app.agents.crews.document_agents import *
from app.agents.crews.document_tasks import *
from crewai import Crew

from app.utils.json_parser import safe_json_load
from app.utils.retry import with_retry

MAX_RETRIES = 2


def classification_decision(state):
    if state.classification_confidence is None:
        return "failed"

    if state.classification_confidence < 0.6:
        return "low_confidence"

    return "proceed"


def extraction_decision(state):
    if state.extraction_confidence is None:
        return "failed"

    if state.extraction_confidence < 0.7:
        return "low_confidence"

    if state.validation_issues:
        return "issues"

    return "clean"


def load_document(state: WorkflowState) -> WorkflowState:
    return state


def classify_document(state: WorkflowState) -> WorkflowState:
    crew = Crew(
            agents=[classifier_agent],
            tasks=[classification_task(classifier_agent, state.document_text)],
            verbose=True
        )
    
    def run(s):
        result = crew.kickoff()
        
        parsed = safe_json_load(result.raw)

        state.document_type = parsed["document_type"]
        state.classification_confidence = parsed["confidence"]
        return s

    return with_retry(state, run, "classify_retries", MAX_RETRIES)


def extract_data(state: WorkflowState) -> WorkflowState:
    crew = Crew(
        agents=[extraction_agent],
        tasks=[
            extraction_task(
                extraction_agent,
                state.document_text,
                state.document_type
            )
        ],
        verbose=True
    )

    result = crew.kickoff()
    parsed = safe_json_load(result.raw)

    state.extracted_data = parsed["data"]
    state.extraction_confidence = parsed["confidence"]

    return state


def validate_data(state: WorkflowState) -> WorkflowState:
    crew = Crew(
        agents=[validation_agent],
        tasks=[validation_task(validation_agent, state.extracted_data)],
        verbose=True
    )

    result = crew.kickoff()
    parsed = safe_json_load(result.raw)

    state.validation_issues = parsed["issues"]
    return state


def route_document(state: WorkflowState) -> WorkflowState:
    if state.classification_confidence is not None and state.classification_confidence < 0.6:
        state.routing_decision = "human_review"
    elif state.validation_issues:
        state.routing_decision = "human_review"
    elif state.extraction_confidence is not None and state.extraction_confidence < 0.7:
        state.routing_decision = "human_review"
    else:
        state.routing_decision = "auto_approved"

    state.status = "completed"
    return state


def build_workflow():
    graph = StateGraph(WorkflowState)

    graph.add_node("load", load_document)
    graph.add_node("classify", classify_document)
    graph.add_node("extract", extract_data)
    graph.add_node("validate", validate_data)
    graph.add_node("route", route_document)

    graph.set_entry_point("load")

    graph.add_edge("load", "classify")

    graph.add_conditional_edges(
        "classify",
        classification_decision,
        {
            "proceed": "extract",
            "low_confidence": "route",
            "failed": END
        }
    )

    graph.add_edge("extract", "validate")

    graph.add_conditional_edges(
        "validate",
        extraction_decision,
        {
            "clean": "route",
            "issues": "route",
            "low_confidence": "route",
            "failed": END
        }
    )

    graph.add_edge("route", END)

    return graph.compile()