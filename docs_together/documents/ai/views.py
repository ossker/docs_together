import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from documents.decorators import owner_or_collaborator_required
from documents.models import Document, DocumentAiSummary
from django.utils import timezone

def call_gemini_api(text):
    api_key = "AIzaSyAgrXmDDpajd326Hz_Eo_GuYf1Ixy1q1vk"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    prompt = (
        "Stwórz bardzo zwięzłe, spójne podsumowanie tego dokumentu. "
        "Zwróć WYŁĄCZNIE końcowe, ogólne podsumowanie w formie ciągłego tekstu — "
        "bez tabel, list, nagłówków, ani żadnych dopisków. "
        "Nie dodawaj wprowadzenia, tytułu ani komentarzy.\n\n"
        f"{text}"
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"Gemini API error: {r.status_code} {r.text}")
    j = r.json()
    return j['candidates'][0]['content']['parts'][0]['text'].strip()


@login_required
@owner_or_collaborator_required
@require_POST
def summarize(request, document_id):
    try:
        data = json.loads(request.body or "{}")
        text = (data.get("text") or "").strip()
        if not text:
            return JsonResponse({"ok": False, "error": "empty_text"}, status=400)

        result = call_gemini_api(text)

        document = Document.objects.get(id=document_id)

        DocumentAiSummary.objects.update_or_create(
            document=document,
            defaults={
                "summary_text": result,
                "updated_by": request.user,
                "updated_at": timezone.now(),
                "created_at": timezone.now(),
            },
        )

        return JsonResponse({"ok": True, "result": result})
    except Exception as e:
        import logging; logging.getLogger(__name__).exception("AI summarize error")
        return JsonResponse({"ok": False, "error": str(e)}, status=500)