from langchain_openai import ChatOpenAI
from momopedia.state import MomoState, ArticleSchema
from momopedia.prompts.personas import AUTHOR_PROMPT

llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

structured_llm = llm.with_structured_output(ArticleSchema)

def author_node(state: MomoState):
    """The author agent logic"""
    print("Authoring article...")

    # Get the history of the conversation
    messages = [{"role": "system", "content": AUTHOR_PROMPT}] + state["messages"]

    # MESSAGE: Let's bin tools here for web search later
    response = structured_llm.invoke(messages)

    return {
            "article": response,
            "messages": [f"Author generated draft: {response['title']}"],
            "next_step": "reviewer",
            "iteration": state.get("iteration", 0) + 1
        }