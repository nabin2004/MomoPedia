import struct
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field 
from momopedia.state import MomoState 
from momopedia.prompts.personas import REVIEWER_PROMPT

class ReviewResult(BaseModel):
    decision: str = Field(description="'revise' or 'approve'")
    feedback: List[str] = Field(description="List of feedback points for the author")

llm = ChatOpenAI(model_name="gpt-4", temperature=0.1) # Low temp for consistency
structured_llm = llm.with_structured_output(ReviewResult)

def reviewer_node(state: MomoState):
    print("---Dr. Spicy is tasting the draft---")

    article_content = state["article"]
    messages = [
        {"role": "system", "content": REVIEWER_PROMPT},
        {"role": "user", "content": f"Please review this article: {article_content}"}    
    ]

    response = structured_reviewer.invoke(messages)
    next_step = "author" if response.decision == "revise" else "chair"

    return {
        "feedback": [response.feedback],
        "messages": [f"Reviewer Decision: {response.decision}. Feedback: {response.feedback}"],
        "next_step": next_step
    }