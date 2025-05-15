from pydantic import BaseModel, Field
from typing import List, Dict, Any, TypedDict, Annotated, Literal
from langgraph.graph import MessagesState

class ChecklistItem(BaseModel):
    category: str = Field(description="Category of the checklist item")
    item: str = Field(description="Description of the checklist item")
    completed: bool = Field(description="Whether the item is completed")
    reason: str = Field(description="Reason why the item is marked as completed or not")

class Recommendation(BaseModel):
    title: str = Field(description="Title of the recommendation")
    description: str = Field(description="Detailed description of how to implement the recommendation")
    priority: int = Field(description="Priority level from 1 (highest) to 5 (lowest)")

class GraphState(MessagesState): #TypedDict):
    content: str  
    content_type: str 
    keywords: List[Dict]  
    checklist: List[Dict] 
    keyword_analysis: Dict 
    structure_analysis: Dict 
    checklist_evaluation: List[ChecklistItem] 
    recommendations: List[Recommendation] 
    overall_score: float  # Overall score
    messages: List[MessagesState]
    tool_calls_result: Any
    pass_fail: Literal["PASS", "FAIL"]  