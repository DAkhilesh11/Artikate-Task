from django.contrib import admin
from django.urls import path
from knowledge_assistant.views import home, DocumentUploadView, AskQuestionView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('upload-document/', DocumentUploadView.as_view(), name='upload-document'),
    path('ask-question/', AskQuestionView.as_view(), name='ask-question'),
]
