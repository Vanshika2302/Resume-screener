"""FastAPI backend. Run: uvicorn main:app --reload"""
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402

from screener import pdf_to_text, screen_resume  # noqa: E402

app = FastAPI(title="Resume Screener")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/screen")
async def screen(resumes: list[UploadFile] = File(...), jd: str = Form(...)):
    """Screen one or more PDF resumes against a job description, ranked by match score."""
    results = []
    for f in resumes:
        entry = {"filename": f.filename}
        try:
            text = pdf_to_text(f.file)
            if not text:
                raise ValueError("No text found (scanned PDF? needs OCR)")
            entry.update(screen_resume(text, jd))
        except Exception as e:
            entry.update({"error": str(e), "match_score": -1})
        results.append(entry)
    if not results:
        raise HTTPException(400, "No resumes uploaded")
    results.sort(key=lambda r: r["match_score"], reverse=True)
    return {"results": results}
