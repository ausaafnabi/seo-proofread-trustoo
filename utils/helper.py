import re
import docx
import pandas as pd

def read_docx(file_path: str) -> str:
    """Read the content of a .docx file."""
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def read_excel(file_path: str) -> pd.DataFrame:
    """Read the content of an Excel file."""
    return pd.read_excel(file_path)

def detect_page_type(content: str) -> str:
    """
    Detect whether the content a cost page or a city page.
    input: content [str]
    returns: cost/city [Literal]
    """

    # Naive algorithm to check it based on patterns
    cost_patterns = [
        r"wat kost",
        r"kosten",
        r"prijs",
        r"betaal",
        r"euro",
        r"€"
    ]
    
    city_patterns = [
        r"in [A-Z][a-z]+",  # "in Amsterdam", "in Utrecht", etc.
        r"beste [a-z]+ in",  # "beste loodgieters in", etc.
        r"vind [a-z]+ in"   # "vind elektriciens in", etc.
    ]
    
    # check the sum of count of all the patterns (simple and slick[maybe require more patterns])
    cost_matches = sum(1 for pattern in cost_patterns if re.search(pattern, content.lower()))
    city_matches = sum(1 for pattern in city_patterns if re.search(pattern, content))
    
    return "cost" if cost_matches > city_matches else "city"