from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from url_features import analyze_email_urls
from sender_features import analyze_sender

model = joblib.load("model.pkl")
tfidf = joblib.load("tfidf.pkl")

app = FastAPI(title="PhishGuard AI API")

RISK_WORDS = ["verify", "account", "click", "claim", "free", "urgent",
              "suspended", "password", "winner", "confirm", "update"]

WORDCLOUD_WORDS = [
    "money", "investment", "bank", "dollars", "pills", "link",
    "online", "security", "offer", "stock", "price", "million",
    "internet", "website", "address", "save", "info", "receive"
]

class EmailRequest(BaseModel):
    sender: str = ""
    subject: str = ""
    body: str = ""

@app.post("/analyze")
def analyze(email: EmailRequest):
    text = email.subject + " " + email.body

    pred = model.predict(tfidf.transform([text]))[0]
    prob = model.predict_proba(tfidf.transform([text]))[0]
    model_confidence = int(prob[1] * 100)

    flags = [w for w in RISK_WORDS if w in text.lower()]
    url_results = analyze_email_urls(text)
    sender_flags = analyze_sender(email.sender)
    wc_hits = [w for w in WORDCLOUD_WORDS if w in text.lower()]

    text_score = min(50 if len(flags) >= 3 else 25 if len(flags) >= 1 else 0 + len(flags) * 5, 50)
    
    url_score = 0
    for r in url_results:
        if "trusted domain" in r["flags"]:
            continue
        if any("impersonating" in f for f in r["flags"]):
            url_score += 30
        if "shortened link" in r["flags"]:
            url_score += 15
        if "no HTTPS" in r["flags"]:
            url_score += 10
    url_score = min(url_score, 50)

    sndr_score = 0
    for f in sender_flags:
        if "impersonating" in f:
            sndr_score += 30
        elif "suspicious word" in f:
            sndr_score += 15
        elif "numbers" in f:
            sndr_score += 10
    sndr_score = min(sndr_score, 50)

    wc_score = min(len(wc_hits) * 3, 15)

    total_score = min(
        int(model_confidence * 0.4) +
        int((text_score * 2) * 0.25) +
        int((url_score * 2) * 0.2) +
        int((sndr_score * 2) * 0.15) +
        wc_score,
        100
    )

    if total_score >= 80:
        verdict = "PHISHING"
    elif total_score >= 50:
        verdict = "SUSPICIOUS"
    else:
        verdict = "LEGITIMATE"

    return {
        "verdict": verdict,
        "total_score": total_score,
        "model_confidence": model_confidence,
        "text_score": text_score,
        "url_score": url_score,
        "sender_score": sndr_score,
        "suspicious_words": flags,
        "pattern_words": wc_hits,
        "sender_flags": sender_flags,
        "url_flags": [f"{r['domain']}: {f}" for r in url_results for f in r["flags"] if f != "trusted domain"]
    }

@app.get("/")
def root():
    return {"message": "PhishGuard AI API", "docs": "/docs"}