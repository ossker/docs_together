from celery import shared_task
from django.utils import timezone
from documents.models import Document

from documents.ai.views import call_gemini_api
from django.utils.html import strip_tags

@shared_task
def generate_summaries():
    docs = Document.objects.filter(summary_pending=True)

    for doc in docs:
        if doc.date_edited < timezone.now() - timezone.timedelta(seconds=60):

            try:
                cleaned_text = strip_tags(doc.content)
                result = call_gemini_api(cleaned_text)
            except Exception:
                continue

            doc.summary_text = result
            doc.summary_pending = False
            doc.summary_updated_at = timezone.now()
            doc.save(update_fields=["summary_text", "summary_pending", "summary_updated_at"])
