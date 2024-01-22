import json
from itertools import cycle
from django.core.management.base import BaseCommand
from teachers.transformers.translation_download import translate_es_en
from teachers.transformers.embeddings_download import (
    fcfmcourses_similarity_calculator,
    guidedthesis_similarity_calculator,
    teacher_similarity_calculator,
    scholarworks_similarity_calculator,
    get_embeddings_of_model,
)

from teachers.openalex_extractor.extractor_script import (
    convert_input_format,
    transformation,
)


class Command(BaseCommand):
    help = "Ejemplo de pipeline de la tarea a resolver."

    def handle(self, *args, **options):
        # example_input = (
        #     "Geolocalización de aparatos móviles perdidos mediante redes de IoT"
        # )
        # example_input = "EXTRACCIÓN DE ATRIBUTOS VISUALES EN PRENDAS DE VESTIR A TRAVÉS DE NEURONAS OCULTAS DE MODELOS CONVOLUCIONALES"
        # example_input = "Interpreting Tabular Classification with Large Language Models: Decision Trees, Neural Networks and Transparency"
        # example_input = "Optimización y Seguridad en Redes de Sensores Inalámbricos para Aplicaciones de Internet de las Cosas (IoT): Un Enfoque Basado en Algoritmos de Aprendizaje Profundo"
        # example_input = "Optimización de Algoritmos de Análisis de Variantes Genéticas para la Predicción y Personalización de Tratamientos Médicos en Medicina Genómica"
        # example_input = "SISTEMA DE RECOMENDACIÓN DE ROPA BASADA EN ARTÍCULOS COMPLEMENTARIO USANDO REDES CONVOLUCIONALES"
        # example_input = "Plataforma de visualización de grafos de la web con RDF"

        # np.set_printoptions(suppress=True)

        example_input = input(
            self.style.SUCCESS(
                "Escriba el título de una memoria o un pequeño resumen de lo que trata:\n"
            )
        )

        top_n_teachers = 5

        # Se traduce al inglés para pasarlo al extractor.
        translated_input = translate_es_en(example_input)

        # Se pasa al extractor y se obtienen las keywords asociadas.
        formatted_input = convert_input_format(translated_input)
        extractor_output = json.loads(transformation(formatted_input))

        tagged_concepts = extractor_output[0]["tags"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Conceptos que el extractor pudo inferir del input: \n {tagged_concepts}\n"
            )
        )

        all_rankings = []

        # Lista profes con keyword más similar a cada concepto
        for concept in tagged_concepts:
            teachers_rank = teacher_similarity_calculator(concept, 3, 5)
            all_rankings.append(teachers_rank)
            # print(f"Concepto: {concept}\nRank: {teachers_rank}\n\n")

        selected_teachers = {}

        # Tomo el primero de cada lista, y si ya están en la lista
        # final, tomó el segundo de esa lista, y así sucesivamente
        # hasta completar los top_n_teachers.
        # Se aprovecha el diccionario ya ordenado.
        for ranking in cycle(all_rankings):
            if len(selected_teachers) == top_n_teachers:
                break
            for teacher, value in ranking.items():
                if teacher not in selected_teachers:
                    selected_teachers[teacher] = value
                    break

        # self.stdout.write(self.style.SUCCESS(f"Lista final: {selected_teachers}\n"))

        sorted_list = sorted(
            selected_teachers.items(), key=lambda x: x[1][0], reverse=False
        )

        print(f"\nLista ordenada de top {top_n_teachers} docentes: \n")
        for teacher_tuple in sorted_list:
            self.stdout.write(
                self.style.SUCCESS(
                    f"{teacher_tuple[0]}\nScore: {teacher_tuple[1][0]}\nKeywords: {teacher_tuple[1][1]}\n"
                )
            )

        # Con los profes de esta lista, busco los cursos similares a la keyword.
        for item in sorted_list:
            teacher = item[0]
            related_kw = item[1][1]

            teacher_courses = fcfmcourses_similarity_calculator(teacher, 5, related_kw)
            print(f"Cursos relacionados de {teacher}:\n{teacher_courses}\n")

            teacher_guided_thesis = guidedthesis_similarity_calculator(
                teacher, 5, related_kw
            )
            print(
                f"Tesis/memorias relacionadas de {teacher}: {teacher_guided_thesis}\n"
            )

            teacher_publications = scholarworks_similarity_calculator(
                teacher, 5, related_kw
            )
            print(f"Publicaciones relacionadas de {teacher}: {teacher_publications}\n")
