import os

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

    @staticmethod
    def get_summary_prompt(text):
        return f"""
                <chapter_text>
                {text}
                </chapter_text>
                Thank you for providing the sample chapter and additional context. I understand that the goal is to develop an agent that can effectively rewrite the content for individuals with dyslexia and ADHD, while maximizing the output within the model's token limit. To achieve this, I recommend the following adjustments to the prompt:

                <prompt>
                Please rewrite the given chapter text in a way that is easier for individuals with dyslexia and ADHD to read and understand. Ensure the rewritten content:

                1. Uses simple, clear, and concise language.
                2. Breaks down complex concepts into smaller, manageable parts.
                3. Utilizes bullet points, numbered lists, and short paragraphs to improve readability.
                4. Includes suggestions for visual aids (e.g., diagrams, illustrations, or flowcharts) to support understanding, described within [Visual Aid: ...] brackets.
                5. Emphasizes key terms, definitions, and important concepts using *bold text*.
                6. Provides explicit connections between ideas and concepts to maintain coherence.
                7. Offers examples and analogies to relate new information to familiar concepts.
                8. Maintains the core information and learning objectives of the original chapter.

                Please ensure the rewritten chapter is comprehensive and does not omit essential information. If the rewritten content exceeds the token limit, prioritize the most critical information and concepts.

                After providing the rewritten chapter, generate a list of questions to check the reader's understanding, including a mix of easy, medium, and complex questions. Organize the questions as follows:

                <questions>
                Easy:
                1. [Question 1]
                2. [Question 2]
                ...

                Medium:
                1. [Question 1]
                2. [Question 2]
                ...

                Complex:
                1. [Question 1]
                2. [Question 2]
                ...
                </questions>

                Generate as many questions as possible within the token limit to assess the reader's understanding of the chapter comprehensively.
                </prompt>
                """


class AnthropicApiClient(ApiClient):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.client = Anthropic(api_key=self.api_key)

    def generate_summary(self, text, model_name):
        prompt = self.get_summary_prompt(text)
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
        prompt = self.get_summary_prompt(text)
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
        prompt = self.get_summary_prompt(text)
        return self.get_completion(prompt, model_name)

    def get_completion(self, prompt, model_name):
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text


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
        heading_style = styles["Heading1"]
        normal_style = styles["Normal"]

        # Add the chapter name as a heading
        chapter_name = os.path.splitext(os.path.basename(file_path))[0]
        elements.append(Paragraph(chapter_name, heading_style))
        elements.append(Spacer(1, 12))  # Add some space after the heading

        # Split the summary into sections
        sections = summary.split("\n\n")
        for section in sections:
            # Add each section as a paragraph
            elements.append(Paragraph(section, normal_style))
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
    input_folder ="data/split_books/Nonverbal Communication in Human Interaction.pdf"
    num_chapters = 2
    start_chapter = 1

    summarizer = PdfSummarizer(api_client)
    summarizer.summarize_chapters(input_folder, num_chapters, start_chapter, model_name)


if __name__ == "__main__":
    main()