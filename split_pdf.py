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
book_name = "Mark L. Knapp, Judith A. Hall, Terrence G. Horgan - Nonverbal Communication in Human Interaction (2013, Wadsworth Publishing).pdf"
input_pdf_file = f"data/books/{book_name}" 
output_directory = f"data/split_books/{book_name}"  
chapter_splits = {
    "chapter 1": "3-28",
    "chapter 2": "29-58",
    "chapter 3": "59-88",
    "chapter 4": "91-122",
    "chapter 5": "123-150",
    "chapter 6": "153-196",
    "chapter 7": "199-230",
    "chapter 8": "231-257",
    "chapter 9": "258-294",
    "chapter 10": "295-322",
    "chapter 11": "323-356",
    "chapter 12": "359-394",
    "chapter 13": "395-420",
}


split_pdf_by_chapters(input_pdf_file, output_directory, chapter_splits)