from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from momopedia.state import MomoState
from momopedia.prompts.personas import CHAIR_PROMPT

class ChairDecision(BaseModel):
    decision: str = Field(description="'ACCEPTED' or 'REJECTED'")
    memo: str = Field(description="Final editorial notes for the public record")

llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_chair = llm.with_structured_output(ChairDecision)

def chair_node(state: MomoState):
    print("--- CHAIR OF THE BOARD IS REVIEWING FINAL DRAFT ---")
    
    # The Chair looks at the WHOLE history (messages) and the feedback
    messages = [
        {"role": "system", "content": CHAIR_PROMPT},
        {"role": "user", "content": f"Final Article: {state['article']}\n\nReviewer Feedback: {state['feedback']}"}
    ]
    
    response = structured_chair.invoke(messages)
    
    return {
        "messages": [f"CHAIR DECISION: {response.decision}. Memo: {response.memo}"],
        "chair_decision": response.decision,
        "next_step": "end"
    }