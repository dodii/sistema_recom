import requests


# Aquí va la conexión al repositorio de académicos que construyó Ignacio.

# No es necesario mantener la url como secreto, pero puede
# ser que después lo guarde como variable de ambiente.
academic_repository_url = "http://143.110.227.147/api/v1"
academic_repository_headers = {
    "content-Type": "application/json",
    "accept": "application/json",
}

"""
Esta función devolverá un diccionario con la información de todos los docentes del DCC.
La llave de cada docente es su id proveniente del repo.
El repositorio entrega a los docentes con los siguientes campos:
id, dblp_id, nombre, unidad, institución, institución_sigla, nombre_externo
"""


def make_request_to_repository_api():
    teachers = {}
    institution = "UChile"

    try:
        response = requests.get(
            academic_repository_url
            + f"/buscar/academico/avanzada?institucion={institution}",
            headers=academic_repository_headers,
        )
        response.raise_for_status()

        # Lo hago de esta forma porque si primero hago institucion = Universidad de Chile,
        # también devuelve cualquier otra institución que tenga Universidad y Chile en su nombre.
        # De esta manera filtro exactamente lo que quiero.
        for teacher in response.json()["academicos"]:
            if teacher["institución"] == "Universidad de Chile":
                teachers[teacher["id"]] = teacher  # Los guardamos por su id

    except requests.exceptions.HTTPError as e:
        print(e.response.text)  # type: ignore

    return teachers
