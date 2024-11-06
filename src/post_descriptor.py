import os
from transformers import pipeline
from rich.console import Console

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

console = Console()

#Load the summarizer pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

class Summarizer:
    def __init__(self):
        pass

    def generate_summary(self, post_content):
        # Generate a summary of the post content
        summary = summarizer(post_content, do_sample=False)
        return summary[0]['summary_text']