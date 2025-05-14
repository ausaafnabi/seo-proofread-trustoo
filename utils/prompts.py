keyword_prompt="""
        You are an expert SEO keyword analyzer. You need to evaluate the usage of keywords in a {content_type} page.
        
        # Content:
        {content}
        
        # Target Keywords:
        {keywords}
        
        Analyze how well the keywords are used in the content. Focus on:
        1. Keyword density
        2. Placement in headings, introduction, and conclusion
        3. Natural usage
        4. Distribution throughout the content
        
        Format your response as a JSON object with the following structure:
        {schema}

        Important only return the schema response as stringified json!!
        """

keyword_output = """
        {
            "keyword_usage":{  
                "keyword1": { 
                    "occurrences": 5,
                    "heading_usage": true/false,
                    "intro_usage": true/false,
                    "conclusion_usage": true/false,
                    "natural_usage": true/false,
                    "assessment": "Brief assessment of usage"
                }
                ...
            }
            "overall_keyword_score": 85, // percentage
            "strengths": ["strength1", "strength2", ...],
            "weaknesses": ["weakness1", "weakness2", ...]
        }
    """
structure_data="""
    {
        "heading_structure": {
            "h1_count": 1,
            "h2_count": 5,
            "h3_count": 8,
            "heading_hierarchy_proper": bool,
            "assessment": "Brief assessment of heading structure"
        },
        "readability": {
            "avg_paragraph_length": 3.5, # sentences
            "readability_score": 75, # percentage
            "assessment": "Brief assessment of readability"
        },
        "formatting": {
            "bullet_points_used": bool,
            "tables_used": bool,
            "bold_text_used": bool,
            "assessment": "Brief assessment of formatting"
        },
        "overall_structure_score": 85, // percentage
        "strengths": ["strength1", "strength2", ...],
        "weaknesses": ["weakness1", "weakness2", ...]
    }
    """
structure_prompt= """
        You are an expert SEO content structure analyzer. You need to evaluate the structure of a {content_type} page.
        
        # Content:
        {content}
        
        Analyze the structure of the content. Focus on:
        1. Heading hierarchy (H1, H2, H3, etc.)
        2. Paragraph length and readability
        3. Use of bullet points, tables, and formatting
        4. Content organization and flow
        5. Presence of meta information
        
        Format your response as a JSON object with the following structure:
        ```
        {data}
        ```
        Important only return the schema response as stringified json!!
        """

checklist_data= """
        [    
            {
                "category": "Category name",
                "item": "Checklist item description",
                "completed": true/false,
                "reason": "Detailed explanation"
            },
            ...
        ]
"""

checklist_prompt="""
        You are an expert SEO content evaluator and proficient dutch speaker. You need to evaluate a {content_type} page against a checklist.
        If required use web search, internal tools etc. Use your skill to the best of your effort.
        # Content:
        {content}
        
        # Keyword Analysis:
        {keyword_analysis}
        
        # Structure Analysis:
        {structure_analysis}
        
        # Checklist Items:
        {checklist}
        
        Evaluate each checklist item and determine if it's completed. Provide a clear reason for your decision.
        
        Format your response as a JSON array of checklist item evaluations (Make sure that all checklist items are evaluated):
        ```
        {data_output}
        ```

        Make sure to cover all the checklist in the output!!!
        Important! strictly follow the schema for JSON array of checklist item evaluations, no modifications in schema!!
 """

recommendation_data="""
        [
            {
                "title": "Brief recommendation title",
                "description": "Detailed description of how to implement the recommendation",
                "priority": 1-5 (1 being highest priority)
            },
            ...
        ]
"""

recommendation_prompt="""
        You are an expert SEO content optimizer. Based on the evaluations, generate up to 5 specific recommendations for improving the content.
        
        # Content Type:
        {content_type}
        
        # Keyword Analysis:
        {keyword_analysis}
        
        # Structure Analysis:
        {structure_analysis}
        
        # Checklist Evaluation:
        {checklist_evaluation}
        
        Generate up to 5 specific, actionable recommendations for improving the content, focusing on the most important issues.
        Prioritize issues that have the biggest impact on SEO performance.
        
        Format your response as a JSON array of recommendations:
        {data_output}

        Important! strictly follow the schema for JSON array of checklist item evaluations, no modifications in schema!
"""