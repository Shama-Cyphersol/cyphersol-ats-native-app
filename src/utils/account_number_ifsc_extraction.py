import pdfplumber
import re

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                return text.strip() if text else None
            else:
                print(f"No pages found in {pdf_path}")
                return None
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None


# Data extraction function for account number and ifsc code
def extract_info(raw_text):
    acc_pattern = r"\b\d{10,18}\b"  # Pattern for account number
    ifsc_pattern = r"\b[A-Z]{4}0[A-Z0-9]{6}\b"  # Pattern for IFSC code

    if not raw_text:  # If raw_text is None or empty, return None values
        return {"acc": None, "ifsc": None}

    # Search for account number and IFSC code
    acc = re.search(acc_pattern, raw_text)
    ifsc = re.search(ifsc_pattern, raw_text)

    return {
        "acc": acc.group(0).strip() if acc else None,
        "ifsc": ifsc.group(0).strip() if ifsc else None
    }

def extract_accno_ifsc(pdf_path):
    raw_text = extract_text_from_pdf(pdf_path)
    data = extract_info(raw_text)
    return data


# # to run single pdf
# pdf_path = "Aiyaz hdf 23.pdf"
# raw_text = extract_text_from_pdf(pdf_path)
# data = extract_info(raw_text)
# print(data)
