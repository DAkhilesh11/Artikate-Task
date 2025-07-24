from django.contrib import admin
from .models import Document, DocumentChunk, QALog

admin.site.register(Document)
admin.site.register(DocumentChunk)
admin.site.register(QALog)
