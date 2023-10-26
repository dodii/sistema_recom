import json
import requests
from sist_recom.settings import UCAMPUS_USER, UCAMPUS_PASSWORD

# Aquí van las requests a U-Campus
# La request solo funciona desde la IP del servidor del DCC, que fue registrada
# por U-Campus, junto con estas credenciales.
url_persona = f"https://{UCAMPUS_USER}:{UCAMPUS_PASSWORD}@ucampus.uchile.cl/api/0/fcfm_ucurriculum/persona?rut="


"""
Esta función...
"""


def get_person_info(rut):
    data = {}
    try:
        response = requests.get(url_persona + rut, verify=True)
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        print(e.response.text)

    return data
