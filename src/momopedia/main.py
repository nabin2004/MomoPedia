from langgraph.graph import StateGraph, END
from momopedia.state import MomoState
from momopedia.agents.author import author_node
from momopedia.agents.reviewer import reviewer_node
from momopedia.agents.chair import chair_node

workflow = StateGraph(MomoState)

workflow.add_node("author", author_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("chair", chair_node)
workflow.set_entry_point("author")

workflow.add_edge("author", "reviewer")


def route_after_review(state: MomoState):
    if state["iteration"] >= 3:
        return "chair" # Send to chair for final call if we're looping too much
    
    if state["next_step"] == "author":
        return "author"
    
    return "chair" # If reviewer approves, go to chair

workflow.add_conditional_edges(
    "reviewer",
    route_after_review,
    {
        "author": "author",
        "chair": "chair"
    }
)

workflow.add_edge("chair", END)

app = workflow.compile()