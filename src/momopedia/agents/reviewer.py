import struct
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Union
from momopedia.state import MomoState 
from momopedia.prompts.personas import REVIEWER_PROMPT
from momopedia.llm import get_llm  

llm = get_llm()

class ReviewResult(BaseModel):
    decision: str = Field(description="'revise' or 'approve'")
    feedback: Union[str, List[str]]  

structured_reviewer = llm.with_structured_output(ReviewResult)

def reviewer_node(state: MomoState):
    print("---Dr. Spicy is tasting the draft---")

    article_content = state["article"]

    print("Article: ", article_content)
    # quit()
    messages = [
        {"role": "system", "content": REVIEWER_PROMPT},
        {"role": "user", "content": f"Please review this article: {article_content}"}    
    ]

    response = structured_reviewer.invoke(messages)
    next_step = "author" if response.decision == "REVISED" else "chair"

    return {
        "feedback": [response.feedback],
        "messages": [f"Reviewer Decision: {response.decision}. Feedback: {response.feedback}"],
        "next_step": next_step
    }