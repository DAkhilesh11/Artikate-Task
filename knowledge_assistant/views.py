from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DocumentSerializer, QuestionSerializer
from .models import DocumentChunk, QALog
from .utils import get_embedding, get_faiss_index, get_faiss_id_map
import pickle
import numpy as np
from transformers import pipeline

# Use flan-t5-base for compatibility with 8GB RAM
qa_llm = pipeline("text2text-generation", model="google/flan-t5-base")

def home(request):
    if request.headers.get('accept') == 'application/json':
        return JsonResponse({"message": "Welcome to the Knowledge Assistant API"})
    return HttpResponse("""
        <html>
            <head>
                <title>Knowledge Assistant API</title>
            </head>
            <body style="background-color:#181818; color:#fff; font-family:sans-serif; text-align:center; margin-top:100px;">
                <h1>Welcome to the Knowledge Assistant API</h1>
                <a href="/admin/" style="display:inline-block; margin-top:30px; padding:15px 30px; background:#007bff; color:#fff; border-radius:8px; text-decoration:none; font-size:1.2em;">
                    Login to Admin
                </a>
            </body>
        </html>
    """)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def build_prompt(chunks, question):
    context = "\n\n".join([c[1].chunk_text for c in chunks])
    prompt = (
        f"Context:\n{context}\n\n"
        f"Based only on the above context, write a detailed, multi-sentence answer to the following question. "
        f"Your answer should be a full paragraph (at least 4-5 sentences), using all relevant information, and should not repeat section numbers or headings. "
        f"Explain as if teaching a high school student, and include examples if possible.\n"
        f"Q: {question}\nA:"
    )
    return prompt

class DocumentUploadView(APIView):
    def post(self, request, format=None):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AskQuestionView(APIView):
    def post(self, request, format=None):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data['question']
            q_emb = get_embedding(question)
            # Use FAISS for fast retrieval
            embedding_dim = len(q_emb)
            index = get_faiss_index(embedding_dim)
            id_map = get_faiss_id_map()
            if len(id_map) == 0 or index.ntotal == 0:
                return Response({"answer": "No knowledge base available.", "sources": []})
            D, I = index.search(np.array(q_emb, dtype='float32').reshape(1, -1), 3)  # Use top 3 chunks for richer context
            chunk_ids = [int(id_map[i]) for i in I[0] if i < len(id_map)]
            from .models import DocumentChunk, QALog
            chunks = [DocumentChunk.objects.get(id=cid) for cid in chunk_ids]
            top_chunks = [(1 - D[0][i], chunks[i]) for i in range(len(chunks))]
            if not top_chunks:
                return Response({"answer": "No relevant answer found.", "sources": []})
            prompt = build_prompt(top_chunks, question)
            llm_output = qa_llm(prompt, max_new_tokens=350, num_return_sequences=1)[0]['generated_text']
            answer = llm_output.strip()
            sources = [f"{c[1].document.file.name} - Page {c[1].page_number}" for c in top_chunks]
            # Log the Q&A
            QALog.objects.create(question=question, answer=answer, sources=", ".join(sources))
            return Response({"answer": answer, "sources": sources})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
