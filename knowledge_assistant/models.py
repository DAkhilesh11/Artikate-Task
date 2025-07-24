from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import extract_pdf_chunks, get_embedding, get_faiss_index, save_faiss_index, get_faiss_id_map, save_faiss_id_map
import pickle
import os
import numpy as np

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_text = models.TextField()
    page_number = models.IntegerField(null=True, blank=True)
    embedding = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chunk from {self.document.title} (Page {self.page_number})"

class QALog(models.Model):
    question = models.TextField()
    answer = models.TextField()
    sources = models.TextField()  # Store as comma-separated or JSON string
    timestamp = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=Document)
def process_document(sender, instance, created, **kwargs):
    if created:
        ext = os.path.splitext(instance.file.name)[-1].lower()
        chunks = []
        if ext == '.pdf':
            chunks = extract_pdf_chunks(instance.file.path)
        elif ext == '.md' or ext == '.txt':
            with open(instance.file.path, 'r', encoding='utf-8') as f:
                text = f.read()
                # Simple chunking: split by paragraphs
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                for i, para in enumerate(paragraphs):
                    chunks.append({'text': para, 'page_number': i + 1})
        # Prepare for FAISS
        id_map = get_faiss_id_map().tolist()
        index = None
        for chunk in chunks:
            embedding = get_embedding(chunk['text'])
            doc_chunk = DocumentChunk.objects.create(
                document=instance,
                chunk_text=chunk['text'],
                page_number=chunk['page_number'],
                embedding=pickle.dumps(embedding)
            )
            # Add to FAISS
            embedding_np = np.array(embedding).astype('float32')
            if index is None:
                index = get_faiss_index(embedding_np.shape[0])
            index.add(embedding_np.reshape(1, -1))
            id_map.append(doc_chunk.id)
        if index is not None:
            save_faiss_index(index)
            save_faiss_id_map(np.array(id_map, dtype=np.int64))
