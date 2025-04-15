import os
import json
from pdfminer.high_level import extract_text
import fitz

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    formatted_pages = []

    for i, page in enumerate(doc):
        text = page.get_text("text")  # Layout-aware line-based extraction
        formatted_pages.append(f"Page {i+1}:\n{text.strip()}")

    full_text = "\n\n".join(formatted_pages)
    
    return full_text


def extract_text_from_pdf_old(pdf_path: str) -> str:
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""
    
def save_results(results, output_dir):
    os.makedirs(output_dir, exist_ok=True)
        
    for path, data in results.items():
        filename = os.path.basename(path).split('.')[0] + "_extracted.json"
        output_path = os.path.join(output_dir, filename)
            
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
                
        print(f"Saved extraction results to {output_path}")