from langchain_openai import ChatOpenAI
from momopedia.state import MomoState, ArticleSchema
from momopedia.prompts.personas import AUTHOR_PROMPT
from momopedia.tools.web_research import search_momo_facts
from momopedia.llm import get_llm
import json

llm = get_llm()

tools = [search_momo_facts]


llm_with_tools = llm.bind_tools(tools)
structured_llm =  llm_with_tools.with_structured_output(ArticleSchema)

def author_node(state: MomoState):
    """The author agent logic"""
    print("Authoring article...")

    # Get the history of the conversation
    messages = [{"role": "system", "content": AUTHOR_PROMPT}] + state["messages"]

    # MESSAGE: Let's bin tools here for web search later
    response = structured_llm.invoke(messages)
    print("RESPONSE: ", response.keys())
    print("TYPE: ", type(response))

    return {
            "article": response["Content"],
            "messages": [f"Author generated draft: {response['Title']}"],
            "next_step": "reviewer",
            "iteration": state.get("iteration", 0) + 1
        }