from pydantic import BaseModel, Field
from typing import List, Dict, Any, TypedDict, Annotated, Literal

class ChecklistItem(BaseModel):
    category: str = Field(description="Category of the checklist item")
    item: str = Field(description="Description of the checklist item")
    completed: bool = Field(description="Whether the item is completed")
    reason: str = Field(description="Reason why the item is marked as completed or not")

class Recommendation(BaseModel):
    title: str = Field(description="Title of the recommendation")
    description: str = Field(description="Detailed description of how to implement the recommendation")
    priority: int = Field(description="Priority level from 1 (highest) to 5 (lowest)")

class GraphState(TypedDict):
    content: str  # The content to analyze
    content_type: str  # 'cost' or 'city'
    keywords: List[Dict]  # List of keywords
    checklist: List[Dict]  # List of checklist items
    keyword_analysis: Dict  # Analysis of keyword usage
    structure_analysis: Dict  # Analysis of content structure
    checklist_evaluation: List[ChecklistItem]  # Evaluation of each checklist item
    recommendations: List[Recommendation]  # List of recommendations
    overall_score: float  # Overall score
    pass_fail: Literal["PASS", "FAIL"]  # Overall assessment