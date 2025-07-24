import os
import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load the model once at module level for efficiency
hf_model = SentenceTransformer('all-MiniLM-L6-v2')
FAISS_INDEX_PATH = "faiss.index"
FAISS_ID_MAP_PATH = "faiss_id_map.npy"

def extract_pdf_chunks(file_path):
    chunks = []
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # Split by paragraphs (double newlines or single newlines)
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                if len(paragraphs) == 1:
                    # If no double newlines, try single newline
                    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
                for para in paragraphs:
                    # Remove section numbers/headings at the start
                    cleaned = para.lstrip('0123456789.() ').strip()
                    chunks.append({'text': cleaned, 'page_number': i + 1})
    return chunks

def get_embedding(text):
    # Returns a numpy array
    embedding = hf_model.encode(text)
    return embedding

def get_faiss_index(dimension):
    try:
        index = faiss.read_index(FAISS_INDEX_PATH)
    except Exception:
        index = faiss.IndexFlatL2(dimension)
    return index

def save_faiss_index(index):
    faiss.write_index(index, FAISS_INDEX_PATH)

def get_faiss_id_map():
    if os.path.exists(FAISS_ID_MAP_PATH):
        return np.load(FAISS_ID_MAP_PATH)
    return np.array([], dtype=np.int64)

def save_faiss_id_map(id_map):
    np.save(FAISS_ID_MAP_PATH, id_map)






