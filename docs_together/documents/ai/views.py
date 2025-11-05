import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from documents.decorators import owner_or_collaborator_required
from documents.models import Document

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
    data = json.loads(request.body or "{}")
    text = (data.get("text") or "").strip()
    if not text:
        return JsonResponse({"ok": False, "error": "empty_text"}, status=400)

    try:
        result = call_gemini_api(text)
    except Exception:
        return JsonResponse({"ok": False, "error": "Błąd komunikacji z API"}, status=500)

    doc = Document.objects.get(id=document_id)
    doc.summary_text = result
    doc.save(update_fields=["summary_text"])

    return JsonResponse({"ok": True, "result": result})