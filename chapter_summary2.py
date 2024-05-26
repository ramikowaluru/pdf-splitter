import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from pypdf import PdfReader
import google.generativeai as genai
import openai
from anthropic import Anthropic

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
        Please provide a concise summary of the given chapter text.
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
            self.save_summary_to_file(summary, output_file_path)
            print(f"Summary saved to {output_file_path}")


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
        model_name = "text-davinci-002"
    elif api_choice == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        api_client = GoogleApiClient(api_key)
        model_name = "gemini-1.5-flash"
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