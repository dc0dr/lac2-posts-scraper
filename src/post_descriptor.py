import os
import ollama
from rich.console import Console


console = Console()


class Summarizer:
    def __init__(self):
        pass

    def generate_summary(self, post_content):
        
        #Load the summarizer pipeline
        summary = ollama.chat(model='llama3.2', messages=[
            {
                'role': 'user',
                'content': f'Summarize this post concisely and result you give me must be nothing but the summarized post: {post_content}'
            }
        ])
        
        # Generate a summary of the post content 
        return summary['message']['content']