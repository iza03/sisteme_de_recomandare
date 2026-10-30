# Laboratoarele 2 și 3 — Sistem de recomandare cu Recombee

Proiectul defineste proprietatile unui catalog de filme si incarca item-urile
in Recombee, folosind SDK-ul oficial pentru Python.

## Dataset

Fisierul `imdb_top_1000.csv` contine 1.000 de filme si seriale IMDb. Pentru
fiecare titlu sunt disponibile informatii precum genul, ratingul, descrierea,
regizorul, durata, numarul de voturi si linkul posterului. Dataset-ul a fost
descarcat de pe Kaggle: **IMDb Movies Dataset — Top 1000 Movies and TV Shows**.

Proprietatile inregistrate in Recombee sunt:

| Proprietate | Tip Recombee | Descriere |
| --- | --- | --- |
| `Series_Title` | `string` | Titlul filmului sau serialului |
| `Genre` | `string` | Genul sau genurile productiei |
| `IMDB_Rating` | `double` | Ratingul IMDb |
| `Overview` | `string` | Descrierea productiei |
| `Director` | `string` | Numele regizorului |
| `Runtime` | `string` | Durata, in formatul din dataset (de exemplu `142 min`) |
| `No_of_Votes` | `int` | Numarul voturilor IMDb |
| `Poster_Link` | `string` | URL-ul posterului |

Datasetul original nu contine o coloana ID. A fost adaugata coloana `item_id`,
cu valori unice de la `imdb-0001` la `imdb-1000`. Aceasta este mapata la
campul nativ `itemId` din Recombee si nu este declarata ca proprietate.

## Instalare si configurare

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Credencialele se configureaza in terminal si nu se salveaza in repository:

```bash
export RECOMBEE_DATABASE_ID="id-ul-bazei-development"
export RECOMBEE_PRIVATE_TOKEN="tokenul-privat"
export RECOMBEE_REGION="eu-west"
```

Pentru definirea proprietatilor din laboratorul 2 se ruleaza:

```bash
python recombee_properties.py
```

## Laboratorul 3 — Incarcarea item-urilor

Scriptul `recombee_items.py` valideaza datasetul si unicitatea ID-urilor,
mapeaza cele opt proprietati si trimite cele 1.000 de filme prin cereri
`Batch`, in 10 loturi a cate 100. `cascade_create=True` permite crearea
automata a item-urilor care nu exista deja.

Scriptul poate fi rulat dintr-un mediu virtual activ, dupa configurarea
variabilelor `RECOMBEE_DATABASE_ID`, `RECOMBEE_PRIVATE_TOKEN` si
`RECOMBEE_REGION`:

```bash
python recombee_items.py
```

La final, scriptul citeste catalogul din Recombee si afiseaza numarul de
item-uri impreuna cu trei exemple, pentru verificare.

Cele 1.000 de item-uri au fost incarcate cu succes in baza de date Recombee
Development, folosind 10 cereri Batch.
