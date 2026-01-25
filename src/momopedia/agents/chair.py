from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from momopedia.state import MomoState
from momopedia.prompts.personas import CHAIR_PROMPT
from momopedia.llm import get_llm  

class ChairDecision(BaseModel):
    Decision: str = Field(description="'ACCEPTED' or 'REJECTED'")
    Memo: str = Field(default="No memo provided", description="Final editorial notes")


llm = get_llm()
structured_chair = llm.with_structured_output(ChairDecision)

def chair_node(state: MomoState):
    print("--- CHAIR OF THE BOARD IS REVIEWING FINAL DRAFT ---")
    
    # The Chair looks at the WHOLE history (messages) and the feedback
    messages = [
        {"role": "system", "content": CHAIR_PROMPT},
        {"role": "user", "content": f"Final Article: {state['article']}\n\nReviewer Feedback: {state['feedback']}"}
    ]
    
    response = structured_chair.invoke(messages)
    print("RESPONSE: ", response)
    print("TYPE OF RESPONSE: ", response)
    return {
        "messages": [f"CHAIR DECISION: {response.Decision}. Memo: {response.Memo}"],
        "chair_decision": response.Decision,
        "next_step": "end"
    }