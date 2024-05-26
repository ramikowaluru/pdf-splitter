import os
from pypdf import PdfReader
from anthropic import Anthropic
from dotenv import load_dotenv

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL_NAME = "claude-3-opus-20240229"


def get_completion(client, prompt):
    return (
        client.messages.create(
            model=MODEL_NAME,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        .content[0]
        .text
    )


def get_text_from_pdf(pdf_locations):
    texts = []
    for pdf_location in pdf_locations:
        reader = PdfReader(pdf_location)
        number_of_pages = len(reader.pages)
        text = "".join(page.extract_text() for page in reader.pages)
        texts.append(text)
    return texts


def save_summary_to_file(summary, chapter_path):
    chapter_folder = os.path.dirname(chapter_path)
    chapter_name = os.path.splitext(os.path.basename(chapter_path))[0]
    file_path = os.path.join(chapter_folder, f"{chapter_name}_summary.pdf")

    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate(file_path, pagesize=letter)

    # Create a list to store the elements of the PDF
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    heading_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # Add the chapter name as a heading
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


def get_the_chapter_summary_prompt(text):
    return f"""
<chapter_text>
{text}
</chapter_text>
your response should be 3000 words at least
Part 1: Dyslexia-Friendly Summary
Please rewrite the chapter text in a way that is easier for a person with dyslexia to read and understand. Ensure that the rewritten content:

1. Uses simple, clear, and concise language.
2. Breaks down complex concepts into smaller, more manageable parts.
3. Utilizes bullet points, numbered lists, and short paragraphs to improve readability.
4. Includes suggestions for visual aids such as diagrams, illustrations, or flowcharts to support understanding. Describe these suggestions within [Visual Aid: ...] brackets.
5. Emphasizes key terms, definitions, and important concepts using *bold text*.
6. Provides explicit connections between ideas and concepts to maintain coherence.
7. Offers examples and analogies to relate new information to familiar concepts.
8. Maintains the core information and learning objectives of the original chapter.

Please ensure that the rewritten chapter is comprehensive and does not omit any essential information. Enclose the dyslexia-friendly summary within <dyslexia_friendly_summary> tags.

Part 2: Learning Questions
After providing the dyslexia-friendly summary, please generate a list of questions to check the reader's understanding of the chapter. Include a mix of easy, medium, and complex questions. Organize the questions in the following format:

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

Please make sure to generate as many questions as possible to comprehensively assess the reader's understanding of the chapter.
"""


# User input for chapter locations and number of chapters to process
input_folder = "data/split_books/Mark L. Knapp, Judith A. Hall, Terrence G. Horgan - Nonverbal Communication in Human Interaction (2013, Wadsworth Publishing).pdf"
num_chapters = 4
file_format = "txt"

chapter_locations = [
    os.path.join(input_folder, f"chapter {i}.pdf") for i in range(7, 7 + num_chapters)
]
# Process chapters and generate summaries

texts = get_text_from_pdf(chapter_locations)
for chapter_path, text in zip(chapter_locations, texts):
    prompt = get_the_chapter_summary_prompt(text)
    summary = get_completion(client, prompt)
    save_summary_to_file(summary, chapter_path)
