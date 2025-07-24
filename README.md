# LLM-Powered Knowledge Assistant API

Welcome to your own AI-powered Knowledge Assistant! This project lets you upload your own PDFs, Markdown, or text files and ask questions about them. The assistant uses advanced language models (LLMs) and retrieval techniques to give you accurate, context-based answers—no hallucinations, just real knowledge from your documents.

## Features
- **Upload PDFs, Markdown, or Text**: Add your own knowledge base via the Django admin.
- **Retrieval-Augmented Generation (RAG)**: Combines fast vector search (FAISS) with a local LLM (flan-t5-base) for detailed, context-aware answers.
- **Secure API**: Token-based authentication for all endpoints.
- **Q&A Logging**: Every question and answer is logged for review.
- **Multi-file Support**: Search across all your uploaded documents.

## Project Architecture
- **Backend**: Django + Django REST Framework
- **LLM**: HuggingFace Transformers (flan-t5-base)
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **Vector Search**: FAISS
- **Authentication**: DRF Token Auth

## Setup Instructions
1. **Clone the repo**
   ```bash
   git clone repo_link
   cd repo-folder
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the server**
   ```bash
   python manage.py runserver
   ```

## Uploading Documents
- Go to `http://127.0.0.1:8000/` and click **Login to Admin**.
- Upload PDFs, Markdown, or Text files under **Documents**.
- The system will automatically parse, chunk, embed, and index your files for search.

## Authentication
- Generate a token for your user:
  ```bash
  python manage.py drf_create_token username
  ```
- Use this token in the `Authorization` header for all API requests:
  ```
  Authorization: Token generated_token (Key: value) -> add in the header section if using postman
  ```

## Asking Questions
- Send a POST request to `/ask-question/` with your question:
  ```json
  {
    "question": "What is the law of gravitation?"
  }
  ```
- The API will return a detailed answer and the sources (file and page).

## Sample Query (using curl)
```bash
curl -X POST http://127.0.0.1:8000/ask-question/ \
     -H "Authorization: Token generated_token" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the law of gravitation?"}'
```

## Sample Data
- Place your sample PDFs or text files in a `sample_data` folder.

## Key Tech Stack
- Django, DRF, HuggingFace Transformers, SentenceTransformers, FAISS

## API Endpoints
- `POST /ask-question/` — Ask a question about your knowledge base

## Security
- All endpoints require a valid token.
- Only authenticated users can upload or ask questions.

## For Developers
- All Q&A interactions are logged in the `QALog` model which admin can view
- Easily extend with new file types, LLMs, or a frontend.


