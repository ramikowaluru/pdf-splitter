# please curate this working code
from PyPDF2 import PdfReader, PdfWriter
import os

def split_pdf_by_chapters(input_pdf, output_folder, splits):
    """
    Splits a PDF into multiple PDFs based on chapter names and page ranges.
    Each chapter's PDF will have page numbers starting from 1.

    Args:
        input_pdf (str): Path to the input PDF file.
        output_folder (str): Path to the folder where output PDFs will be saved.
        splits (dict): A dictionary where keys are chapter names and values are
                      page ranges as strings (e.g., "3-28", "31-54").
    """
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    with open(input_pdf, 'rb') as infile:
        pdf_reader = PdfReader(infile)

        for chapter_name, page_range in splits.items():
            start_page, end_page = parse_page_range(page_range)

            output_filename = f"{output_folder}/{chapter_name}.pdf"
            pdf_writer = PdfWriter()

            for page in range(start_page - 1, end_page):
                pdf_writer.add_page(pdf_reader.pages[page])

            with open(output_filename, 'wb') as outfile:
                pdf_writer.write(outfile)

def parse_page_range(page_range_str):
    if '-' in page_range_str:
        return map(int, page_range_str.split('-'))
    else:
        start_page = int(page_range_str)
        return start_page, start_page + 1

# Example usage:
book_name = "The Winding Road from the Late Teens Through the Twenties-Oxford University Press (2014).pdf"
input_pdf_file = f"data/books/{book_name}"
output_directory = f"data/split_books/{book_name}"

chapter_splits = {
    "chapter 1": "20-48",
    "chapter 2": "49-67",
    "chapter 3": "68-101",
    "chapter 4": "102-132",
    "chapter 5": "133-160",
    "chapter 6": "161-187",
    "chapter 7": "188-212",
    "chapter 8": "213-229",
    "chapter 9": "230-262",
    "chapter 10": "263-284",
    "chapter 11": "285-309",
    "chapter 12": "310-329",
    "chapter 13": "330-350",
}

split_pdf_by_chapters(input_pdf_file, output_directory, chapter_splits)