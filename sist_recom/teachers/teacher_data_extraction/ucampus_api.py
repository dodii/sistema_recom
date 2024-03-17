import requests
from sist_recom.settings import UCAMPUS_USER, UCAMPUS_PASSWORD

# Aquí van las requests a U-Campus
# La request SOLAMENTE FUNCIONARÁ DESDE IP DE LA MÁQUINA VIRTUAL DEL DCC, que fue registrada
# por U-Campus, junto con estas credenciales.

# Estos son algunos de los endpoints.
url_person = f"https://{UCAMPUS_USER}:{UCAMPUS_PASSWORD}@ucampus.uchile.cl/api/0/fcfm_ucurriculum/persona?rut="

academic_info_url = f"https://{UCAMPUS_USER}:{UCAMPUS_PASSWORD}@ucampus.uchile.cl/api/0/fcfm_ucurriculum/grupo_personas?grupo=fcfm.ciencias_computacion"

"""
Esta función obtiene todos los elementos relacionados al trabajo de cada docente.
Entre estos hay publicaciones, memorias, cursos, etc.
"""


def get_person_info(rut):
    data = {}
    try:
        response = requests.get(url_person + rut, verify=True)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.HTTPError as e:
        print(e.response.text)  # type: ignore

    return data


"""
Esta función entrega la información de docentes de jornada completa y parcial.
Los externos/expertos no vienen en esta lista.

"""


def get_academics_group():
    data = {}
    try:
        response = requests.get(academic_info_url, verify=True)  # type: ignore
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.HTTPError as e:
        print(e.response.text)  # type: ignore

    return data
