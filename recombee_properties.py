"""Defineste in Recombee proprietatile catalogului de filme IMDb."""

import os
import sys

import pandas as pd
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import AddItemProperty, ListItemProperties
from recombee_api_client.exceptions import APIException


PATH_DATASET = "imdb_top_1000.csv"

# Numele proprietatilor coincid cu numele coloanelor din CSV. Identificatorul
# unic nu este inclus: Recombee il gestioneaza separat, sub numele itemId.
PROPRIETATI_CATALOG = [
    {"name": "Series_Title", "type": "string"},
    {"name": "Genre", "type": "string"},
    {"name": "IMDB_Rating", "type": "double"},
    {"name": "Overview", "type": "string"},
    {"name": "Director", "type": "string"},
    {"name": "Runtime", "type": "string"},
    {"name": "No_of_Votes", "type": "int"},
    {"name": "Poster_Link", "type": "string"},
]


def load_dataset():
    """Citeste CSV-ul si verifica cerintele laboratorului si schema aleasa."""
    try:
        df = pd.read_csv(PATH_DATASET)
    except FileNotFoundError:
        print(f"Eroare: fisierul '{PATH_DATASET}' nu a fost gasit.")
        return None
    except pd.errors.ParserError as error:
        print(f"Eroare la citirea CSV-ului: {error}")
        return None

    total_randuri = len(df)
    print(f"Dataset incarcat cu succes. Total randuri: {total_randuri}")

    if not 100 <= total_randuri <= 10_000:
        print("Eroare: dataset-ul trebuie sa contina intre 100 si 10.000 de item-uri.")
        return None

    coloane_necesare = {prop["name"] for prop in PROPRIETATI_CATALOG}
    coloane_lipsa = sorted(coloane_necesare - set(df.columns))
    if coloane_lipsa:
        print(f"Eroare: lipsesc coloanele: {', '.join(coloane_lipsa)}")
        return None

    print("\nPrimele 3 randuri:")
    print(df.head(3).to_string(index=False))
    print("-" * 50)
    return df


def create_client():
    """Construieste clientul din credencialele pastrate in variabile de mediu."""
    database_id = os.getenv("RECOMBEE_DATABASE_ID")
    private_token = os.getenv("RECOMBEE_PRIVATE_TOKEN")
    region_name = os.getenv("RECOMBEE_REGION", "eu-west").lower()

    if not database_id or not private_token:
        print(
            "Eroare: seteaza RECOMBEE_DATABASE_ID si RECOMBEE_PRIVATE_TOKEN "
            "in terminal inainte de rulare."
        )
        return None

    regions = {
        "ap-se": Region.AP_SE,
        "ca-east": Region.CA_EAST,
        "eu-west": Region.EU_WEST,
        "us-west": Region.US_WEST,
    }
    region = regions.get(region_name)
    if region is None:
        print(
            f"Eroare: regiunea '{region_name}' nu este valida. "
            f"Alege una dintre: {', '.join(regions)}."
        )
        return None

    return RecombeeClient(database_id, private_token, region=region)


def set_properties(client):
    """Trimite schema catalogului catre Recombee."""
    print("\nSe definesc proprietatile in Recombee...")

    for prop in PROPRIETATI_CATALOG:
        try:
            client.send(AddItemProperty(prop["name"], prop["type"]))
            print(f"[OK] {prop['name']} ({prop['type']}) a fost adaugata.")
        except APIException as error:
            if "already exists" in str(error).lower():
                print(f"[OK] {prop['name']} exista deja.")
            else:
                print(f"[EROARE] {prop['name']}: {error}")


def verify(client):
    """Listeaza proprietatile active din baza de date Recombee."""
    print("\nProprietatile active in Recombee:")
    try:
        proprietati_active = client.send(ListItemProperties())
        for prop in proprietati_active:
            print(f"- {prop['name']} => {prop['type']}")
    except APIException as error:
        print(f"Verificarea a esuat: {error}")


def main():
    if load_dataset() is None:
        return 1

    client = create_client()
    if client is None:
        return 1

    set_properties(client)
    verify(client)
    return 0


if __name__ == "__main__":
    sys.exit(main())
