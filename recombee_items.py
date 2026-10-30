"""Incarca in Recombee catalogul de filme IMDb, folosind cereri Batch."""

import os
import sys

import pandas as pd
from requests.exceptions import RequestException
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import Batch, ListItems, SetItemValues
from recombee_api_client.exceptions import APIException


PATH_DATASET = "imdb_top_1000.csv"
ID_COLUMN = "item_id"
BATCH_SIZE = 100

PROPERTY_COLUMNS = [
    "Series_Title",
    "Genre",
    "IMDB_Rating",
    "Overview",
    "Director",
    "Runtime",
    "No_of_Votes",
    "Poster_Link",
]


def load_dataset():
    """Citeste si valideaza datasetul inaintea trimiterii."""
    try:
        df = pd.read_csv(PATH_DATASET)
    except (FileNotFoundError, pd.errors.ParserError) as error:
        print(f"Eroare la citirea datasetului: {error}")
        return None

    if not 100 <= len(df) <= 10_000:
        print("Eroare: datasetul trebuie sa aiba intre 100 si 10.000 de item-uri.")
        return None

    required_columns = {ID_COLUMN, *PROPERTY_COLUMNS}
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        print(f"Eroare: lipsesc coloanele: {', '.join(missing_columns)}")
        return None

    if df[ID_COLUMN].isna().any() or (df[ID_COLUMN].astype(str).str.strip() == "").any():
        print(f"Eroare: coloana {ID_COLUMN} contine ID-uri goale.")
        return None

    if df[ID_COLUMN].duplicated().any():
        duplicates = df.loc[df[ID_COLUMN].duplicated(), ID_COLUMN].tolist()[:5]
        print(f"Eroare: ID-uri duplicate: {duplicates}")
        return None

    print(f"Dataset validat: {len(df)} item-uri cu ID-uri unice.")
    return df


def create_client():
    """Construieste clientul folosind credencialele din variabilele de mediu."""
    database_id = os.getenv("RECOMBEE_DATABASE_ID")
    private_token = os.getenv("RECOMBEE_PRIVATE_TOKEN")
    region_name = os.getenv("RECOMBEE_REGION", "eu-west").lower()

    if not database_id or not private_token:
        print("Eroare: lipsesc RECOMBEE_DATABASE_ID sau RECOMBEE_PRIVATE_TOKEN.")
        return None

    regions = {
        "ap-se": Region.AP_SE,
        "ca-east": Region.CA_EAST,
        "eu-west": Region.EU_WEST,
        "us-west": Region.US_WEST,
    }
    region = regions.get(region_name)
    if region is None:
        print(f"Eroare: regiunea '{region_name}' nu este valida.")
        return None

    return RecombeeClient(database_id, private_token, region=region)


def row_to_properties(row):
    """Mapeaza un rand CSV la proprietatile definite in laboratorul 2."""
    return {
        "Series_Title": str(row["Series_Title"]),
        "Genre": str(row["Genre"]),
        "IMDB_Rating": float(row["IMDB_Rating"]),
        "Overview": str(row["Overview"]),
        "Director": str(row["Director"]),
        "Runtime": str(row["Runtime"]),
        "No_of_Votes": int(row["No_of_Votes"]),
        "Poster_Link": str(row["Poster_Link"]),
    }


def send_batch(client, requests, batch_number):
    """Trimite un lot si verifica erorile individuale din raspuns."""
    responses = client.send(Batch(requests))
    errors = [response for response in responses if response.get("code", 200) >= 400]
    if errors:
        first_error = errors[0]
        raise RuntimeError(
            f"Lotul {batch_number} contine {len(errors)} erori. "
            f"Prima eroare: {first_error}"
        )
    print(f"[OK] Lotul {batch_number}: {len(requests)} item-uri trimise.")


def send_items(client, df):
    """Trimite toate item-urile in loturi de cate 100."""
    requests = []
    batch_number = 0

    try:
        for _, row in df.iterrows():
            item_id = str(row[ID_COLUMN])
            properties = row_to_properties(row)
            requests.append(SetItemValues(item_id, properties, cascade_create=True))

            if len(requests) == BATCH_SIZE:
                batch_number += 1
                send_batch(client, requests, batch_number)
                requests = []

        if requests:
            batch_number += 1
            send_batch(client, requests, batch_number)
    except (APIException, RequestException, RuntimeError) as error:
        print(f"Eroare la trimiterea item-urilor: {error}")
        return False

    print(f"Toate cele {len(df)} item-uri au fost trimise cu succes.")
    return True


def verify(client):
    """Citeste catalogul din Recombee pentru confirmare."""
    try:
        items = []
        page_size = 500
        offset = 0
        while True:
            page = client.send(ListItems(count=page_size, offset=offset))
            items.extend(page)
            if len(page) < page_size:
                break
            offset += len(page)

        examples = client.send(
            ListItems(count=3, return_properties=True, included_properties=PROPERTY_COLUMNS)
        )
    except (APIException, RequestException) as error:
        print(f"Verificarea a esuat: {error}")
        return False

    print(f"\nVerificare Recombee: {len(items)} item-uri existente in catalog.")
    print("Exemple citite inapoi din Recombee:")
    for item in examples:
        print(f"- {item['itemId']}: {item.get('Series_Title', '(fara titlu)')}")
    return True


def main():
    df = load_dataset()
    if df is None:
        return 1

    client = create_client()
    if client is None:
        return 1

    if not send_items(client, df):
        return 1

    return 0 if verify(client) else 1


if __name__ == "__main__":
    sys.exit(main())
