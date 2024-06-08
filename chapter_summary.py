import os
import re

from abc import ABC, abstractmethod

from dotenv import load_dotenv

from pypdf import PdfReader

import google.generativeai as genai
import openai
from anthropic import Anthropic

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate

from prompts import SUMMARY_PROMPT_ANTHROPIC_OPENAI, SUMMARY_PROMPT_GEMINI

load_dotenv()


class ApiClient(ABC):
    def __init__(self, api_key):
        self.api_key = api_key

    @abstractmethod
    def generate_summary(self, text, model_name):
        pass

    @abstractmethod
    def get_completion(self, prompt, model_name):
        pass


class AnthropicApiClient(ApiClient):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.client = Anthropic(api_key=self.api_key)

    def generate_summary(self, text, model_name):
        prompt = SUMMARY_PROMPT_ANTHROPIC_OPENAI.format(text=text)
        return self.get_completion(prompt, model_name)

    def get_completion(self, prompt, model_name):
        return (
            self.client.messages.create(
                model=model_name,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            .content[0]
            .text
        )


class OpenAIApiClient(ApiClient):
    def __init__(self, api_key):
        super().__init__(api_key)
        openai.api_key = self.api_key

    def generate_summary(self, text, model_name):
        prompt = SUMMARY_PROMPT_ANTHROPIC_OPENAI.format(text=text)
        return self.get_completion(prompt, model_name)

    def get_completion(self, prompt, model_name):
        response = openai.Completion.create(
            engine=model_name,
            prompt=prompt,
            max_tokens=2048,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()


class GoogleApiClient(ApiClient):
    def __init__(self, api_key):
        super().__init__(api_key)
        genai.configure(api_key=self.api_key)

    def generate_summary(self, text, model_name):
        prompt = SUMMARY_PROMPT_GEMINI.format(text=text)
        return self.get_completion(prompt, model_name)

    def get_completion(self, prompt, model_name):
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)

        if response.candidates:  # Check if there are any candidates
            return response.text
        else:
            # Handle the case where no candidates are returned (e.g., log an error, retry, etc.)
            print("Error: No candidates returned for the prompt.")
            print("Prompt feedback:", response.prompt_feedback)
            return None


class PdfSummarizer:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_text_from_pdf(self, pdf_locations):
        texts = []
        for pdf_location in pdf_locations:
            reader = PdfReader(pdf_location)
            text = "".join(page.extract_text() for page in reader.pages)
            texts.append(text)
        return texts

    def save_summary_to_file(self, summary, file_path):
        with open(file_path, "w") as file:
            file.write(summary)

    def summarize_chapters(self, input_folder, num_chapters, start_chapter, model_name):
        chapter_locations = [
            os.path.join(input_folder, f"chapter {i}.pdf") for i in range(start_chapter, start_chapter + num_chapters)
        ]

        texts = self.get_text_from_pdf(chapter_locations)
        for chapter_path, text in zip(chapter_locations, texts):
            summary = self.api_client.generate_summary(text, model_name)
            if summary is None:
                print(f"No summary generated for {chapter_path}. Skipping.")
                continue
            chapter_name = os.path.splitext(os.path.basename(chapter_path))[0]
            output_file_path = os.path.join(os.path.dirname(chapter_path), f"{chapter_name}_summary.pdf")
            self.save_summary_to_pdf(summary, output_file_path)
            print(f"Summary saved to {output_file_path}")

    def save_summary_to_pdf(self, summary, file_path):
        # Create a SimpleDocTemplate object
        doc = SimpleDocTemplate(file_path, pagesize=letter)

        # Create a list to store the elements of the PDF
        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        heading1_style = styles["Heading1"]
        heading2_style = styles["Heading2"]
        heading3_style = styles["Heading3"]
        normal_style = styles["Normal"]
        bullet_style = styles["Bullet"]
        bullet_style.leftIndent = 20
        bullet_style.spaceAfter = 10

        # Split the summary into sections
        sections = summary.split("\n")
        for section in sections:
            if section.startswith("## "):
                # Add main headings (Heading1)
                elements.append(Paragraph(section[3:], heading1_style))
                elements.append(Spacer(1, 12))  # Add some space after the heading
            elif section.startswith("### "):
                # Add subheadings (Heading2)
                elements.append(Paragraph(section[4:], heading2_style))
                elements.append(Spacer(1, 12))  # Add some space after the subheading
            elif section.startswith("#### "):
                # Add sub-subheadings (Heading3)
                elements.append(Paragraph(section[5:], heading3_style))
                elements.append(Spacer(1, 12))  # Add some space after the sub-subheading
            else:
                # Split the section into chunks based on special characters
                chunks = re.split(r'(\*\*.*?\*\*|\*.*?\*|• .*)', section)
                for chunk in chunks:
                    if chunk.startswith("**") and chunk.endswith("**"):
                        # Add bold text
                        elements.append(Paragraph(chunk[2:-2], normal_style))
                    elif chunk.startswith("*") and chunk.endswith("*"):
                        # Add italic text
                        elements.append(Paragraph(chunk[1:-1], normal_style))
                    elif chunk.startswith("• "):
                        # Add bullet points
                        elements.append(Paragraph(chunk[2:], bullet_style))
                    elif chunk.strip():
                        # Add normal paragraphs
                        elements.append(Paragraph(chunk, normal_style))
                elements.append(Spacer(1, 12))  # Add some space between sections

        # Build the PDF
        doc.build(elements)


def main():
    # Choose the API client
    api_choice = 'google'

    if api_choice == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        api_client = AnthropicApiClient(api_key)
        model_name = "claude-3-opus-20240229"
    elif api_choice == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        api_client = OpenAIApiClient(api_key)
        model_name = "gpt-4o"
    elif api_choice == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        api_client = GoogleApiClient(api_key)
        model_name = "gemini-1.5-pro"
    else:
        print("Invalid API choice. Exiting.")
        return

    # User input for chapter locations and number of chapters to process
    input_folder = "data/split_books/The Winding Road from the Late Teens Through the Twenties-Oxford University Press (2014).pdf"
    num_chapters = 13
    start_chapter = 1

    summarizer = PdfSummarizer(api_client)
    summarizer.summarize_chapters(input_folder, num_chapters, start_chapter, model_name)


if __name__ == "__main__":
    main()