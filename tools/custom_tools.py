from langchain.tools import tool

@tool("serp_length_tool")
def serp_length_tool(title: str, metadescription: str) -> dict:
    """
    Call this tool to find the length of  Page Title and a Meta Description.
    example result:
    {
        "title_length": 70,
        "metadescription_length": 150
    }
    """
    return {
        "title_length": len(title),
        "metadescription_length": len(metadescription)
    }

