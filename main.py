from bs4 import BeautifulSoup
import requests
import pandas as pd

"""
Script pour récupérer les données concernant la qualité de l'eau des plages du Québec à partir du Programme Environnement-Plage

Source des données: https://www.environnement.gouv.qc.ca/programmes/env-plage/index.asp

Le script récupère les données de toutes les plages de chaque région du Québec et les sauvegarde dans un fichier JSON.
"""


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
        # make tuple with (id, name)
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


def main():
    alltables = []

    for region in get_regions_ids():
        url = f"https://www.environnement.gouv.qc.ca/programmes/env-plage/liste_plage.asp?region={region[0]}"
        try:
            table = get_table(url)
            # add the region name and id to the table
            table["regionid"] = region[0]
            table["regionname"] = region[1]
            alltables.append(table)
        except ValueError:
            print("No table found for region", region[1])
            continue
    # Concatenate all the tables
    df = pd.concat(alltables)
    df.to_json("plages.json", orient="records", force_ascii=False)


if __name__ == "__main__":
    main()
