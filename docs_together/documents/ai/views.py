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

def call_gemini_generate(text_with_marker: str):
    api_key = "AIzaSyAgrXmDDpajd326Hz_Eo_GuYf1Ixy1q1vk"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    prompt = (
        "Masz dokument tekstowy. W miejscu, w którym ma zostać wygenerowany nowy fragment, "
        "znajduje się dokładnie ciąg znaków XXXX.\n"
        "Twoim zadaniem jest zaproponować tekst, który powinien zostać wstawiony w miejsce XXXX, "
        "tak aby dobrze pasował do kontekstu dokumentu (przed i po tym miejscu).\n\n"
        "ZASADY ODPOWIEDZI:\n"
        "- ZWRÓĆ WYŁĄCZNIE gotowy tekst, który należy wstawić w miejsce XXXX.\n"
        "- NIE dodawaj żadnych komentarzy, nagłówków, opisu, znaczników html, wyjaśnień ani oznaczeń typu \"Oto tekst\".\n"
        "- Nie powtarzaj całego dokumentu, jedynie brakujący fragment.\n\n"
        f"DOKUMENT:\n{text_with_marker}"
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
    if not r.ok:
        raise RuntimeError(f"Gemini API error: {r.status_code} {r.text}")
    j = r.json()
    return j["candidates"][0]["content"]["parts"][0]["text"].strip()


@login_required
@owner_or_collaborator_required
@require_POST
def generate_text(request, document_id):
    data = json.loads(request.body or "{}")
    text = (data.get("text") or "").strip()

    if not text:
        return JsonResponse({"ok": False, "error": "empty_text"}, status=400)

    if "XXXX" not in text:
        return JsonResponse({"ok": False, "error": "missing_marker"}, status=400)

    try:
        result = call_gemini_generate(text)
    except Exception:
        return JsonResponse({"ok": False, "error": "Błąd komunikacji z API"}, status=500)

    return JsonResponse({"ok": True, "result": result})

def call_gemini_improve_style(html_content: str) -> str:

    api_key = "AIzaSyAgrXmDDpajd326Hz_Eo_GuYf1Ixy1q1vk"

    if not api_key:
        # jeśli masz klucz wpisany "na sztywno" jak w poprzednim kodzie, możesz zamiast tego:
        # api_key = "TWÓJ_KLUCZ"
        raise RuntimeError("Brak GEMINI_API_KEY")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent"
        f"?key={api_key}"
    )

    prompt = (
        "Otrzymasz zawartość dokumentu w HTML.\n"
        "Twoim zadaniem jest poprawienie błędów językowych i stylistycznych, "
        "z zachowaniem sensu tekstu oraz struktury dokumentu (nagłówki, akapity, listy itd.).\n\n"
        "ZASADY FORMATOWANIA:\n"
        "- Zwróć wynik w HTML.\n"
        "- Fragmenty tekstu, które ZMIENIASZ lub DODAJESZ, otaczaj znacznikiem "
        "<span class=\"ai-style-change\">…</span>.\n"
        "- Fragmenty, których nie zmieniasz, pozostaw IDENTYCZNE jak w wejściu.\n"
        "- Nie dodawaj żadnych komentarzy, opisów ani znaczników spoza treści dokumentu.\n\n"
        "Wejściowy HTML dokumentu:\n\n"
        f"{html_content}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return ""

@require_POST
@login_required
@owner_or_collaborator_required
def improve_style(request, document_id):
    """
    Przyjmuje cały dokument (HTML) i zwraca HTML z poprawionym stylem,
    gdzie zmienione fragmenty są oznaczone <span class="ai-style-change">...</span>.
    """
    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Nieprawidłowe dane wejściowe"}, status=400)

    content = body.get("content", "").strip()
    if not content:
        return JsonResponse({"ok": False, "error": "Brak treści dokumentu"}, status=400)

    Document.objects.filter(pk=document_id).first()

    try:
        improved_html = call_gemini_improve_style(content)
    except requests.RequestException:
        return JsonResponse({"ok": False, "error": "Błąd komunikacji z modelem AI"}, status=502)
    except RuntimeError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    if not improved_html:
        return JsonResponse({"ok": False, "error": "Brak odpowiedzi od AI"}, status=500)

    return JsonResponse(
        {
            "ok": True,
            "styled_html": improved_html,
        }
    )
