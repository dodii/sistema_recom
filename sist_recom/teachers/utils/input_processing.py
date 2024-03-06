import json
from teachers.transformers.translation_download import translate_es_en
from teachers.openalex_extractor.extractor_script import (
    convert_input_format,
    transformation,
)


def extract_input_keywords(title, content):

    translated_title = translate_es_en(title)
    translated_content = translate_es_en(content)

    # Se pasa al extractor y se obtienen las keywords asociadas.
    # formatted_input = convert_input_format(translated_title, translated_content)
    formatted_input = convert_input_format(translated_title, translated_content)
    extractor_output = json.loads(transformation(formatted_input))

    tagged_concepts = extractor_output[0]["tags"]
    scores = extractor_output[0]["scores"]

    return tagged_concepts, scores
