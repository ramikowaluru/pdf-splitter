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

    with open(input_pdf, 'rb') as infile:
        reader = PdfReader(infile)

        for chapter_name, page_range in splits.items():
            if '-' in page_range:
                start_page, end_page = map(int, page_range.split('-'))
            else:
                start_page = int(page_range)
                end_page = start_page + 1

            output_filename = f"{output_folder}/{chapter_name}.pdf"
            writer = PdfWriter()
            
            for page in range(start_page - 1, end_page):
                writer.add_page(reader.pages[page])

            with open(output_filename, 'wb') as outfile:
                writer.write(outfile)

# Example usage:
book_name = "Nonverbal Communication in Human Interaction.pdf"
input_pdf_file = f"data/books/{book_name}" 
output_directory = f"data/split_books/{book_name}"  
chapter_splits = {
    "chapter 1": "23-48",
    "chapter 2": "49-78",
    "chapter 3": "79-108",
    "chapter 4": "111-142",
    "chapter 5": "143-171",
    "chapter 6": "173-216",
    "chapter 7": "219-249",
    "chapter 8": "250-276",
    "chapter 9": "278-314",
    "chapter 10": "315-342",
    "chapter 11": "343-356",
    "chapter 12": "359-394",
    "chapter 13": "395-420",
}


split_pdf_by_chapters(input_pdf_file, output_directory, chapter_splits)