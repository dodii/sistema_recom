import requests

# En este archivo están las funciones encargadas de obtener
# la información desde sitios como OpenAlex o DBLP.
# Son sus trabajos académicos e investigaciones que están alojadas
# en estos sitios.

openalex_api = "https://api.openalex.org/"

"""
Esta función hace una query en función del nombre del docente,
ya que es la forma más directa de buscar a un investigador en 
este sitio. 

La API devuelve a todos los investigadores que hicieron match, a veces
se repite y hay un investigador guardado múltiples veces, o sea que tiene
varios perfiles. Lo conveniente es que uno de sus perfiles está mucho
más completo que los otros, así que se puede trabajar con ese. Esto se
mide con el campo relevance_score, mientras más alto, mejor.

La API de OpenAlex también incluye keywords/conceptos que tratan de caracterizar
al investigador, vienen en el campo x_concepts. Cada concepto trae un score,
mientras más alto, es más probable que esté relacionado de forma coherente
al investigador. De esta forma, se puede filtrar desde cierto score en adelante,
quitando los conceptos que estorben.

Los trabajos están en otro endpoint. Se accede a ellos con el campo works_api_url.
"""


def get_openalex_teacher_data(teacher_display_name):
    api_query = f"{openalex_api}authors?search={teacher_display_name}"
    response = requests.get(api_query)

    # Se hace la request
    try:
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        print(e.response.text)

    return response.json()


"""
Esta función extrae la información de los trabajos de un investigador.
Aparte del título y abstract, tenemos una lista de conceptos/keywords, vienen en el
campo concepts del json. Los conceptos también traen un score, de la misma forma
que se menciona en la función anterior.

Cabe destacar que el abstract, en caso de estar incluido, viene en formato
de índice invertido, por lo que es necesario convertirlo a texto común y corriente.
"""


def get_openalex_works_of_teacher(works_api_url):
    per_page_works = 200

    # Seleccionamos el máximo de trabajos que openalex puede mostrar por página.
    # Es posible pedirlos TODOS pero por ahora no es necesario, son muy pocos
    # los investigadores que tienen tantos trabajos guardados por OpenAlex.
    response = requests.get(works_api_url + f"&per-page={per_page_works}")

    try:
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        print(e.response.text)

    return response.json()
