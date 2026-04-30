import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv("C:/Users/Bernardo/phishguard/data/dataset.csv").dropna(subset=["text"])

X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42
)

tfidf = TfidfVectorizer(max_features=5000, stop_words="english")
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec = tfidf.transform(X_test)

model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_vec, y_train)

print(classification_report(y_test, model.predict(X_test_vec)))

joblib.dump(model, "C:/Users/Bernardo/phishguard/model.pkl")
joblib.dump(tfidf, "C:/Users/Bernardo/phishguard/tfidf.pkl")
print("Modelo salvo!")