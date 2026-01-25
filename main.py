from langgraph.graph import StateGraph, END
from momopedia.state import MomoState
from momopedia.agents.author import author_node
from momopedia.agents.reviewer import reviewer_node

workflow = StateGraph(MomoState)

workflow.add_node("author", author_node)
workflow.add_node("reviewer", reviewer_node)

workflow.set_entry_point("author")

workflow.add_edge("author", "reviewer")


def route_after_review(state: MomoState):
    # This function looks at the state and decides where to go next
    if state["next_step"] == "author":
        # If the reviewer said 'revise', go back to author
        return "author"
    else:
        # If 'approve', we go to the Chair (or END for now)
        return END

workflow.add_conditional_edges(
    "reviewer",
    route_after_review,
    {
        "author": "author",
        "end": END
    }
)

app = workflow.compile()