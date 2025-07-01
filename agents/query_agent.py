from typing import Dict, Any
import google.generativeai as genai
import json
import os
import re

class QueryAgent:
    def __init__(self):
        """Initialize the query agent with Gemini model"""
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format the context for the Gemini model"""
        try:
            
            context_copy = json.loads(json.dumps(context))
            return json.dumps(context_copy, indent=2)
        except Exception as e:
            return f"Error formatting context: {str(e)}"

    def _format_for_slack(self, text: str) -> str:
        """Convert any markdown-style formatting to Slack-friendly format"""
        
        text = re.sub(r'^#{1,6}\s*(.*?)$', r'*\1*', text, flags=re.MULTILINE)
        
        
        text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
        

        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        
        text = re.sub(r'^\s*[\*\-\+]\s+', '• ', text, flags=re.MULTILINE)
        
        
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        
        text = re.sub(r'(?<!\*)\*(?!\*)', '', text)
        
        return text.strip()

    def _create_slack_table(self, data: list, headers: list) -> str:
        """Create a nicely formatted table for Slack using code blocks"""
        if not data or not headers:
            return ""
        
        
        col_widths = [len(str(header)) for header in headers]
        for row in data:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        
        header_row = " | ".join(f"{str(header):<{col_widths[i]}}" for i, header in enumerate(headers))
        separator = "-" * len(header_row)
        
        
        data_rows = []
        for row in data:
            formatted_row = " | ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row))
            data_rows.append(formatted_row)
        
        return f"```\n{header_row}\n{separator}\n" + "\n".join(data_rows) + "\n```"

    def _enhance_with_tables(self, response: str, context: Dict[str, Any]) -> str:
        """Add formatted tables when appropriate"""
        try:
            analysis = context.get("analysis", {})
            if not analysis:
                return response
            
            
            if any(keyword in response.lower() for keyword in ['performance', 'productivity', 'compare', 'rank']):

                table_data = []
                for user, stats in analysis.items():
                    commits = stats.get('commits', 0)
                    lines_added = stats.get('lines_added', 0)
                    lines_deleted = stats.get('lines_deleted', 0)
                    net_lines = lines_added - lines_deleted
                    
                    table_data.append([
                        user,
                        f"{commits}",
                        f"+{lines_added}",
                        f"-{lines_deleted}",
                        f"{net_lines:+d}"
                    ])
                
                table_data.sort(key=lambda x: int(x[1]), reverse=True)
                
                headers = ["Developer", "Commits", "Added", "Deleted", "Net"]
                table = self._create_slack_table(table_data, headers)
                
                response += f"\n\n📊 *Performance Overview*\n{table}"
            
            return response
            
        except Exception as e:
            return response

    def _generate_answer(self, question: str, context: Dict[str, Any]) -> str:
        """Generate an answer using Gemini 2.0 Flash (synchronous)"""
        try:
            system_prompt = """You are an expert development data analyst. Your job is to answer questions about 
            development metrics, code changes, and team activity based on the provided data. 
            
            IMPORTANT FORMATTING RULES:
            - Use *text* for bold (not **text**)
            - Use • for bullet points
            - For tables, provide data in a structured way that can be formatted
            - Keep responses concise and actionable
            - Use emojis appropriately (📊 for metrics, 🏆 for top performers, ⚠️ for issues, etc.)
            - If you don't know something, say so clearly
            
            Make your response friendly and easy to read in Slack."""

            formatted_context = self._format_context(context)
            
            user_prompt = f"""Context:
            {formatted_context}
            
            Question: {question}
            
            Provide a detailed analysis based on the context above. Be specific and include relevant metrics.
            Format your response for Slack with proper *bold* formatting, • bullets, and clear structure.
            If showing comparisons or rankings, organize the information clearly."""

            
            response = self.model.generate_content([
                {"role": "user", "parts": [system_prompt]},
                {"role": "user", "parts": [user_prompt]}
            ])
            
            
            formatted_response = self._format_for_slack(response.text)
            
            
            if any(keyword in question.lower() for keyword in ['compare', 'rank', 'rate', 'productivity', 'performance']):
                formatted_response = self._enhance_with_tables(formatted_response, context)
            
            return formatted_response
            
        except Exception as e:
            return f"❌ Error generating answer: {str(e)}"
    
    def query(self, question: str, context: Dict[str, Any]) -> str:
        """
        Answers a question based on the provided development data context (synchronous)
        """
        if not context:
            return "No data available to answer the question. Please generate a dev report first."
            
        return self._generate_answer(question, context)

def create_query_agent():
    """Factory function to create a query agent"""
    return QueryAgent()