from typing import Annotated, List, TypedDict, Literal
from langchain_core.messages import BaseMessage
import operator

class ArticleSchema(TypedDict):
    title: str
    content: str
    citations: List[str]
    version: float

class MomoState(TypedDict):
    # 'operator.add' allows us to append messages rather than overwrite
    messages: Annotated[List[BaseMessage], operator.add]
    article: ArticleSchema
    feedback: List[str]
    iteration: int
    next_step: Literal["author", "reviewer", "chair", "end"]