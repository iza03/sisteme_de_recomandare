# Laboratorul 5 — Recomandari content-based folosind cosine similarity

## Dataset

Am folosit fisierul `tesco_sample.json`, care contine produse de la
supermarketurile Tesco. Campul cu text este `description`, care contine
descrierea produsului si tag-uri HTML. Dupa eliminarea produselor duplicate
raman 189 de produse.

## Implementare

Scriptul `cosine_similarity.py` este adaptat dupa tutorialul primit:

1. elimina tag-urile HTML din `description`;
2. preproceseaza textul: litere mici, fara cifre si caractere speciale, fara
   stopwords;
3. transforma descrierile in vectori TF-IDF cu `TfidfVectorizer`;
4. calculeaza cosine similarity intre toate produsele cu `cosine_similarity`.

## Matricea de similaritate

Matricea de scoruri (189 x 189) este salvata in `similarity_matrix.csv`.

## Doua produse asemanatoare

**Bondi Sands Aero Self Tanning Foam 225Ml** si
**Bondi Sands 1 Hour Express Foam 225Ml** au cosine similarity **0.9272**.

Perechea are sens: ambele sunt spume autobronzante de la acelasi producator.
Descrierile lor au in comun cuvinte precum *tan*, *foam*, *self tan* si
*coconut*.
