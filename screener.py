"""Core logic: PDF -> text -> LLM extraction -> embedding score -> LLM analysis."""
import json
import os
from functools import lru_cache

from pydantic import BaseModel, ValidationError
from pypdf import PdfReader

PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # "gemini" (free tier) or "anthropic"
DEFAULT_MODELS = {"gemini": "gemini-flash-latest", "anthropic": "claude-sonnet-5-5"}
MODEL = os.getenv("LLM_MODEL", DEFAULT_MODELS.get(PROVIDER, ""))


class Resume(BaseModel):
    name: str
    skills: list[str]
    years_experience: float
    education: str


@lru_cache(maxsize=1)
def _client():
    if PROVIDER == "anthropic":
        from anthropic import Anthropic
        return Anthropic()  
    from google import genai
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@lru_cache(maxsize=1)
def _embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def pdf_to_text(file) -> str:
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def ask_llm(prompt: str, max_tokens: int = 1000) -> str:
    if PROVIDER != "anthropic":
        resp = _client().models.generate_content(model=MODEL, contents=prompt)
        return resp.text or ""
    msg = _client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def parse_json(raw: str) -> dict:
    """Pull the JSON object out of an LLM reply, even if wrapped in ```json fences."""
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM reply")
    return json.loads(raw[start : end + 1])


def extract_resume(text: str, retries: int = 2) -> Resume:
    prompt = f"""Extract info from this resume. Reply with ONLY a JSON object with keys:
name (string), skills (list of strings), years_experience (number), education (string).
Use "Unknown" or 0 if something is missing.

Resume:
{text[:12000]}"""
    last_error = None
    for _ in range(retries + 1):
        try:
            return Resume(**parse_json(ask_llm(prompt)))
        except (ValueError, ValidationError, json.JSONDecodeError) as e:
            last_error = e
    raise RuntimeError(f"Could not extract resume data: {last_error}")


def match_score(resume_text: str, jd_text: str) -> float:
    from sentence_transformers import util
    a, b = _embedder().encode([resume_text, jd_text])
    score = float(util.cos_sim(a, b)) * 100
    return round(max(0.0, min(100.0, score)), 1)


def explain(resume_text: str, jd_text: str) -> str:
    prompt = f"""Compare this resume to the job description.
Give: 3 strengths, 3 skill gaps, and a one-line verdict. Be concise.

JOB DESCRIPTION:
{jd_text[:6000]}

RESUME:
{resume_text[:12000]}"""
    return ask_llm(prompt)


def screen_resume(resume_text: str, jd_text: str) -> dict:
    return {
        "candidate": extract_resume(resume_text).model_dump(),
        "match_score": match_score(resume_text, jd_text),
        "analysis": explain(resume_text, jd_text),
    }
