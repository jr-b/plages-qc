from bs4 import BeautifulSoup
import requests
import pandas as pd
from duckduckgo_search import DDGS
from time import sleep
import random

"""
Script pour récupérer les données concernant la qualité de l'eau des plages du Québec à partir du Programme Environnement-Plage

Source des données: https://www.environnement.gouv.qc.ca/programmes/env-plage/index.asp

Le script récupère les données de toutes les plages de chaque région du Québec et les sauvegarde dans un fichier JSON.
"""


def sleep_random() -> None:
    sleep(1 + 1 * random.random())


def get_regions_ids(
    url: str = "https://www.environnement.gouv.qc.ca/programmes/env-plage/index.asp",
) -> list[tuple[str, str]]:
    """Get the regions ids and name from the main page"""
    response = requests.get(url)
    if not response.ok:
        response.raise_for_status()
    try:
        soup = BeautifulSoup(response.content, "html.parser")
        regions = soup.find("div", {"class": "bte-liste-region"}).find_all(
            "a", href=True
        )
        # make list of tuple with (id, name)
        regions_ids = [(a["href"][-2:], a.text) for a in regions]
        return regions_ids
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_table(url: str) -> pd.DataFrame:
    """Get the table from the url, assuming we want the first table from the webpage"""
    header = ["municipalite", "plagename", "plandeau", "cote", "dernierprelevement"]
    tables = pd.read_html(url, skiprows=[0])
    if len(tables) == 0:
        raise ValueError("No table found")
    tables[0].columns = header
    return tables[0]


def get_url_about_beach(searchstring: str) -> dict[str, str]:
    """
    Query DuckDuckGo for the first result about the beach
    Returns a dictionary with the url of the first result, the title of the page and its description
    """
    sleep_random()
    try:
        with DDGS(proxy="socks5://127.0.0.1:9150", timeout=20) as ddgs:
            for r in ddgs.text(
                searchstring,
                region="ca-fr",
                safesearch="on",
                max_results=1,
                backend="html",
            ):
                return r
    except Exception as e:
        print(f"Error getting url: {e}")
        return {}


def get_image_about_beach(searchstring: str) -> dict[str, str]:
    """
    Query DuckDuckGo for the first image about the beach
    """
    sleep_random()
    try:
        with DDGS(proxy="socks5://127.0.0.1:9150", timeout=20) as ddgs:
            for r in ddgs.images(
                searchstring,
                region="ca-fr",
                layout="Wide",
                size="Large",
                safesearch="on",
                max_results=1,
            ):
                return r
    except Exception as e:
        print(f"Error getting image: {e}")
        return {}


def main():
    alltables = []

    for region in get_regions_ids():
        url = f"https://www.environnement.gouv.qc.ca/programmes/env-plage/liste_plage.asp?region={region[0]}"
        try:
            print("Processing region: ", region[1])
            table = get_table(url)
            # add the region name and id to the table
            table["regionid"] = region[0]
            table["regionname"] = region[1]
            alltables.append(table)
        except ValueError:
            print("No table found for region: ", region[1])
            continue
    # Concatenate all the tables
    df = pd.concat(alltables)
    count = len(df)
    df["id"] = df.index
    for i, row in df.iterrows():
        print("Processing ", i, " of ", count)
        searchstring = f"{row['plagename']} {row['plandeau']} {row['municipalite']}"
        # Get the url of the first result
        result = get_url_about_beach(searchstring)
        if result:
            df.loc[i, "remotecontent"] = result["href"]
        # Get the image of the first result
        result = get_image_about_beach(searchstring)
        if result:
            df.loc[i, "image"] = result["image"]

    df.to_json("plages.json", orient="records", force_ascii=False)


if __name__ == "__main__":
    main()
