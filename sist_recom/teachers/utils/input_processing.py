import json
from teachers.transformers.translation_model import translate_es_en
from teachers.openalex_extractor.extractor_script import (
    convert_input_format,
    transformation,
)
from teachers.models import TeacherKeywordRelationship

"""
La entrada está en texto plano, es traducida al inglés para que el extractor
pueda manejarla mejor, junto con envolverla en un json. Los resultados son
las keywords y sus scores, ordenadas descendentemente. 
"""


def extract_input_keywords(title, content):

    translated_title = translate_es_en(title)
    translated_content = translate_es_en(content)

    # Se pasa al extractor y se obtienen las keywords asociadas.
    formatted_input = convert_input_format(translated_title, translated_content)
    extractor_output = json.loads(transformation(formatted_input))

    tagged_concepts = extractor_output[0]["tags"]
    scores = extractor_output[0]["scores"]

    return tagged_concepts, scores


def get_profile_keywords(teachers):
    return [
        [
            kw.keyword.keyword
            for kw in TeacherKeywordRelationship.objects.filter(teacher=teacher)
        ]
        for teacher in teachers
    ]
