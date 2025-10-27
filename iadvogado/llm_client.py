import os
from typing import Dict
from config import settings

# This client uses OpenAI as example. You can swap to another LLM provider.
import openai
openai.api_key = settings.openai_api_key

SYSTEM_PROMPT = (
    "Você é um assistente que traduz documentos jurídicos brasileiros para linguagem clara e acessível. "
    "Responda em três blocos: 1) O que aconteceu; 2) O que significa; 3) O que fazer agora. "
    "Seja objetivo, use frases curtas e linguagem simples, voltada para leigos e com exemplos quando útil. "
)


async def simplify_text(text: str) -> Dict[str, str]:
    # Build a prompt that asks for a JSON-like output to make parsing trivial
    prompt = (
        "Receba o texto jurídico abaixo e retorne um JSON com as chaves: what_happened, what_it_means, what_to_do_now.\n\n"
        f"TEXTO: {text}\n\n"
        "Lembre-se de ser conciso e claro."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",  # placeholder — change to allowed model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.2,
    )

    # Try to parse output. We expect either JSON or plain text divided in sections.
    raw = response.choices[0].message.content.strip()
    # Best effort parsing — production should be more robust (schema validation)
    # Try to extract JSON
    import json
    try:
        parsed = json.loads(raw)
        return {
            'what_happened': parsed.get('what_happened', ''),
            'what_it_means': parsed.get('what_it_means', ''),
            'what_to_do_now': parsed.get('what_to_do_now', ''),
        }
    except Exception:
        # Fallback: split by headings
        parts = {'what_happened': '', 'what_it_means': '', 'what_to_do_now': ''}
        lowered = raw.lower()
        # naive splits
        import re
        h_match = re.split(r"what (happened|happens|ocorreu)|o que aconteceu", raw, flags=re.I)
        # fallback: divide into three roughly equal parts
        third = len(raw) // 3
        parts['what_happened'] = raw[:third].strip()
        parts['what_it_means'] = raw[third:2*third].strip()
        parts['what_to_do_now'] = raw[2*third:].strip()
        return parts