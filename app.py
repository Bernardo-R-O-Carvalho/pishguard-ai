import subprocess
subprocess.run(["pip", "install", "scikit-learn", "gradio"], check=True)

import gradio as gr
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Treinar modelo
random.seed(42)
rows = []
for _ in range(300):
    if random.random() > 0.5:
        rows.append(("urgent verify account click http immediately free claim suspended password winner", 1))
    else:
        rows.append(("team meeting report attached invoice project update order shipped", 0))

texts, labels = zip(*rows)
tfidf = TfidfVectorizer(max_features=200, stop_words='english')
model = LogisticRegression(random_state=42)
model.fit(tfidf.fit_transform(texts), labels)

def predict(subject, body):
    text = subject + " " + body
    pred = model.predict(tfidf.transform([text]))[0]
    conf = model.predict_proba(tfidf.transform([text]))[0][pred]
    flags = [w for w in ["verify","account","click","claim","free","urgent","http","suspended","password"] if w in text.lower()]
    verdict = "🚨 PHISHING" if pred else "✅ LEGITIMATE"
    return f"{verdict}\nConfidence: {conf*100:.1f}%\nRed Flags: {', '.join(flags[:3]) if flags else 'none'}"

with gr.Blocks() as demo:
    gr.Markdown("# 🛡️ PhishGuard AI\nPaste an email below to check if it's phishing.")
    subject = gr.Textbox(label="Subject")
    body = gr.Textbox(label="Body", lines=4)
    btn = gr.Button("Analyze", variant="primary")
    output = gr.Textbox(label="Result")
    btn.click(predict, inputs=[subject, body], outputs=output)

demo.launch(server_name="0.0.0.0", server_port=8080)
