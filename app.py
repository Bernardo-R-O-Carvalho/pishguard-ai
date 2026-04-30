import gradio as gr
import joblib
from url_features import analyze_email_urls

model = joblib.load("model.pkl")
tfidf = joblib.load("tfidf.pkl")

RISK_WORDS = ["verify", "account", "click", "claim", "free", "urgent",
              "suspended", "password", "winner", "confirm", "update"]

def predict(subject, body):
    text = subject + " " + body

    pred = model.predict(tfidf.transform([text]))[0]
    prob = model.predict_proba(tfidf.transform([text]))[0]
    confidence = prob[pred] * 100

    risk_score = int(confidence if pred == 1 else 100 - confidence)

    flags = [w for w in RISK_WORDS if w in text.lower()]

    url_results = analyze_email_urls(text)
    url_flags = []
    for r in url_results:
        for f in r["flags"]:
            if f != "domínio confiável":
                url_flags.append(f"{r['domain']}: {f}")

    if pred == 1:
        if risk_score >= 90:
            verdict = "🚨 PHISHING — Alto risco"
        else:
            verdict = "⚠️ SUSPEITO — Risco moderado"
    else:
        verdict = "✅ LEGÍTIMO"

    result = f"{verdict}\n"
    result += f"Score de risco: {risk_score}/100\n"
    result += f"\nPalavras suspeitas: {', '.join(flags) if flags else 'nenhuma'}\n"
    result += f"URLs suspeitas: {', '.join(url_flags) if url_flags else 'nenhuma'}\n"

    if url_results:
        result += f"\nURLs encontradas: {len(url_results)}\n"
        for r in url_results:
            status = "✅" if "domínio confiável" in r["flags"] else "⚠️"
            result += f"  {status} {r['domain']}\n"

    return result

with gr.Blocks() as demo:
    gr.Markdown("# 🛡️ PhishGuard AI\nPaste an email below to check if it's phishing.")
    subject = gr.Textbox(label="Subject")
    body = gr.Textbox(label="Body", lines=4)
    btn = gr.Button("Analyze", variant="primary")
    output = gr.Textbox(label="Result", lines=12)
    btn.click(predict, inputs=[subject, body], outputs=output)

demo.launch(server_name="0.0.0.0", server_port=8080)