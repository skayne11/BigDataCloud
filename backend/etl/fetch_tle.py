import requests

CELESTRAK_BASE = "https://celestrak.org/NORAD/elements/gp.php?GROUP={}&FORMAT=tle"

def fetch_tle(group="active"):
    """
    Télécharge les TLEs du groupe demandé (par défaut 'active').
    Retourne le texte brut TLE.
    """
    url = CELESTRAK_BASE.format(group)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.text

if __name__ == "__main__":
    print(fetch_tle()[:300])
