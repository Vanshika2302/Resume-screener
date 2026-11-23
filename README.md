# Resume Screener

Upload one or more PDF resumes, paste a job description, and get a ranked list with a match score, extracted candidate data, and an AI explanation of strengths and gaps.

**Pipeline:** PDF → text (pypdf) → LLM extracts validated JSON (Pydantic) → embedding match score (sentence-transformers) → LLM strengths/gaps → FastAPI → Streamlit UI

## Tech stack
Python, FastAPI, Pydantic, Gemini API (free tier) or Claude API, sentence-transformers, Streamlit, pytest

## Setup
```bash
python -m venv venv && source venv/bin/activate   
pip install -r requirements.txt
cp .env.example .env    # then add your API_KEY
```

## Run
```bash
# Terminal 1 - backend (API docs at http://127.0.0.1:8000/docs)
uvicorn main:app --reload

# Terminal 2 - UI
streamlit run app.py
```

## Test
```bash
pytest
```

## Features
- Multi-resume upload, ranked by match score
- Pydantic-validated extraction with retry on bad LLM JSON
- Graceful errors per file (e.g. scanned PDFs)
- Swappable LLM provider (Gemini free tier or Claude) via `LLM_PROVIDER` and `LLM_MODEL` env vars

## Evaluation (fill this in!)
Tested on __ dummy resumes: skill extraction accuracy ≈ __%. Top-ranked resume matched my manual ranking in __ of __ cases.

## Screenshots
<img width="1920" height="859" alt="Screenshot (1439)" src="https://github.com/user-attachments/assets/1b1cf66c-ade9-49f0-94dd-9c94318daefe" />
<img width="1920" height="864" alt="Screenshot (1441)" src="https://github.com/user-attachments/assets/b7642ed1-cd56-4ed9-b191-5a63cd01b0bf" />

## Limitations
- Scanned/image PDFs need OCR (not included)
- The embedding model reads only the first ~256 tokens, so the score is a rough signal; the LLM analysis is more detailed
- Use dummy resumes only; don't upload real personal data

## Future ideas
Docker, OCR support, skill-overlap scoring, PII masking, bias checks
