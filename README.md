# Laborator 2 — Sistem de recomandare cu Recombee

Proiectul defineste in Recombee proprietatile unui catalog de filme, folosind
SDK-ul oficial pentru Python.

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

Identificatorul unic nu este declarat ca proprietate. Recombee il gestioneaza
nativ ca `itemId` atunci cand item-urile vor fi incarcate intr-un laborator
ulterior.
