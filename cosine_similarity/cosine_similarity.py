"""Laborator 5 - Cosine similarity intre produsele Tesco."""

import html
import json
import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "tesco_sample.json"
MATRIX_PATH = BASE_DIR / "similarity_matrix.csv"
TOP_PAIRS_PATH = BASE_DIR / "top_pairs.csv"
TOP_N = 15

# Cuvinte din sablonul paginilor Tesco
TESCO_BOILERPLATE = {
    "information", "product", "description", "safety", "view", "warning",
    "warnings", "preparation", "usage", "pack", "size", "net", "contents",
    "ingredients", "material", "return", "tesco", "stores", "ltd",
}
STOP_WORDS = list(ENGLISH_STOP_WORDS | TESCO_BOILERPLATE)


def strip_html(raw_html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw_html or "")
    return html.unescape(text)


def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_products(path: Path) -> pd.DataFrame:
    with path.open(encoding="utf-8") as f:
        products = json.load(f)

    df = pd.DataFrame(products)[["sku", "name", "breadcrumbs", "description"]]
    # Eliminare produse duplicate
    df = df.drop_duplicates(subset="sku").drop_duplicates(subset="name").reset_index(drop=True)
    df["clean_description"] = df["description"].map(strip_html)
    df["text"] = (df["name"] + " " + df["clean_description"]).map(preprocess)
    df = df[df["text"].str.len() > 0].reset_index(drop=True)
    return df


def top_similar_pairs(sim: pd.DataFrame, df: pd.DataFrame, n: int) -> pd.DataFrame:
    rows = []
    values = sim.to_numpy()
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            if df.at[i, "text"] == df.at[j, "text"]:
                continue
            rows.append((df.at[i, "name"], df.at[j, "name"], values[i, j]))
    pairs = pd.DataFrame(rows, columns=["product_a", "product_b", "cosine_similarity"])
    return pairs.sort_values("cosine_similarity", ascending=False).head(n)


def main() -> None:
    df = load_products(DATASET_PATH)
    print(f"Produse incarcate: {len(df)}")

    vectorizer = TfidfVectorizer(stop_words=STOP_WORDS, min_df=2, max_df=0.8)
    tfidf = vectorizer.fit_transform(df["text"])
    print(f"Dimensiune vocabular TF-IDF: {len(vectorizer.vocabulary_)}")

    sim = pd.DataFrame(cosine_similarity(tfidf), index=df["name"], columns=df["name"])
    sim.round(4).to_csv(MATRIX_PATH)
    print(f"Matricea de similaritate ({sim.shape[0]}x{sim.shape[1]}) salvata in {MATRIX_PATH.name}")

    pairs = top_similar_pairs(sim, df, TOP_N)
    pairs.round(4).to_csv(TOP_PAIRS_PATH, index=False)
    print(f"\nTop {TOP_N} perechi de produse asemanatoare:")
    for rank, row in enumerate(pairs.itertuples(index=False), start=1):
        print(f"{rank:2}. {row.cosine_similarity:.4f}  {row.product_a}  <->  {row.product_b}")

    example = df.at[0, "name"]
    print(f"\nCele mai asemanatoare 5 produse cu '{example}':")
    print(sim.iloc[0].drop(labels=example, errors="ignore").nlargest(5).round(4).to_string())


if __name__ == "__main__":
    main()
