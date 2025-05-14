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
