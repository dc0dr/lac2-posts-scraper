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
                'content': f'''
                Take this text: {post_content}.
                
                Summarize it in less than fifteen words to focus on the key topics and omit unnecessary details. 
                If the main text is not in English, translate it to English first before summarizing it.
                The result should only be the text you summarized. Do not add anything to it.
                ''',
            }
        ])
        
        # Generate a summary of the post content 
        return summary['message']['content']