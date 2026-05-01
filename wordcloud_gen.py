import os
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

CUSTOM_STOPWORDS = STOPWORDS.union({
    "subject", "will", "one", "now", "time", "may", "make", "need",
    "want", "well", "get", "use", "see", "new", "way", "know", "come",
    "said", "also", "re", "s", "t", "don", "mail", "email", "send",
    "sent", "message", "year", "look", "made", "part", "find", "work",
    "thank", "best", "regard", "please", "would", "could", "like"
})

def generate_wordcloud():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "data", "dataset.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(BASE_DIR, "..", "data", "dataset.csv")

    df = pd.read_csv(csv_path).dropna(subset=["text"])
    spam_df = df[df["label"] == 1]
    text = " ".join(spam_df["text"].tolist())

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="black",
        colormap="Reds",
        max_words=100,
        stopwords=CUSTOM_STOPWORDS
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("wordcloud.png", dpi=150, bbox_inches="tight")
    plt.close()
    return "wordcloud.png"

if __name__ == "__main__":
    generate_wordcloud()
    print("Word cloud saved!")