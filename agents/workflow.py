from langgraph.graph import StateGraph, END
from langgraph.prebuilt import tools_condition, ToolNode

from core.models import GraphState
from core.llmrouter import tools_all
from agents.agents import keyword_analyzer, structure_analyzer,checklist_evaluator,recommendations_generator

def create_workflow():
    """
    Create and return the LangGraph workflow for SEO content checking.
    returns: workflow [StateGraph] compiled
    """
    workflow = StateGraph(GraphState)
    
    # Making a chained graph as 1 process is dependent on another one (mostly)
    workflow.add_node("keyword_analyzer", keyword_analyzer)
    workflow.add_node("structure_analyzer", structure_analyzer)
    workflow.add_node("checklist_evaluator", checklist_evaluator)
    # workflow.add_node("tools", ToolNode(tools_all))
    workflow.add_node("recommendations_generator", recommendations_generator)
    
    workflow.add_edge("keyword_analyzer", "structure_analyzer")
    workflow.add_edge("structure_analyzer", "checklist_evaluator")
    # workflow.add_conditional_edges(
    #     "checklist_evaluator",
    #     tools_condition,
    #     {
    #         "tools": "tools",
    #         "__end__": "recommendations_generator"
    #     }
    # )
    # workflow.add_edge("tools", "checklist_evaluator")
    workflow.add_edge("checklist_evaluator", "recommendations_generator")
    workflow.add_edge("recommendations_generator", END)
    
    # entry point -> analyze keywords
    workflow.set_entry_point("keyword_analyzer")
    
    return workflow.compile()

def print_results(state: GraphState):   
    print(f"\n== Content Evaluation Results ({state['overall_score']:.1f}%) - {state['pass_fail']} ==\n")
    
    print("Checklist Evaluation:")
    for item in state['checklist_evaluation']:
        status = "✅" if item.completed else "❌"
        print(f"{status} {item.category}: {item.item}")
        print(f"   Reason: {item.reason}\n")
    
    print("\nTop Recommendations:")
    sorted_recommendations = sorted(state['recommendations'], key=lambda x: x.priority)
    for i, rec in enumerate(sorted_recommendations, 1):
        print(f"{i}. {rec.title} (Priority: {rec.priority})")
        print(f"   {rec.description}\n")