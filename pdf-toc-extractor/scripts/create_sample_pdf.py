#!/usr/bin/env python3
"""
Create a sample PDF with bookmarks/TOC for testing the extraction script.
Note: This requires reportlab to be installed.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfutils
import os
import sys

def create_sample_pdf_with_toc(output_path):
    """Create a PDF sample with table of contents."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.colors import black, red, blue

        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        # Add some content
        chapters = [
            {"title": "Introduction", "content": "This is the introduction..."},
            {"title": "Chapter 1: Basics", "content": "This covers the basics..."},
            {"title": "Chapter 1.1: Setup", "content": "Setting up the environment..."},
            {"title": "Chapter 1.2: Configuration", "content": "Configuring the system..."},
            {"title": "Chapter 2: Advanced Topics", "content": "Advanced information..."},
            {"title": "Conclusion", "content": "In conclusion..."}
        ]

        for i, chapter in enumerate(chapters):
            c.drawString(100, height - 100, f"Page {i+1}: {chapter['title']}")
            c.drawString(100, height - 120, chapter['content'])
            c.showPage()

        c.save()

        # Note: PyPDF2 bookmark functionality is limited.
        # In real usage, you'd need another library to add proper bookmarks.
        print(f"Sample PDF created at: {output_path}")
        print("Note: PyPDF2 can only extract bookmarks, not create them.")
        print("To test with real bookmarks, use a PDF that already has them.")

    except ImportError:
        print("reportlab not available. Install it with:")
        print("pip install reportlab")
        return False

    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        # Default output path
        output_path = os.path.join(os.path.dirname(__file__), "sample_doc.pdf")

    create_sample_pdf_with_toc(output_path)