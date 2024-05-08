import json
import pandas as pd
import time
import datetime
from django.core.management.base import BaseCommand
from teachers.models import Teacher
from teachers.transformers.translation_model import translate_es_en

from teachers.transformers.embeddings_and_filtering import teacher_similarity_calculator

from teachers.openalex_extractor.extractor_script import (
    convert_input_format,
    transformation,
)


class Command(BaseCommand):
    help = "Test con datos históricos de memorias y guías/co-guías"

    def handle(self, *args, **options):

        start = time.process_time()

        # all_teachers = Teacher.objects.all()
        all_teachers = Teacher.objects.exclude(openalex_id="")

        # contar docentes que fueron recomendados por este sistema.
        teachers_count = {}
        for teacher in all_teachers:
            teachers_count[teacher] = 0

        top_n = 7

        fall_2022 = pd.read_excel("informes_e/datos_otono_2022_keywords_gpt.xlsx")
        spring_2022 = pd.read_excel("informes_e/datos_primavera_2022_keywords_gpt.xlsx")

        total_rows = len(fall_2022) + len(spring_2022)

        success = 0

        # Para calcular recall
        total_ruts = {}

        for i in fall_2022.index:
            teacher1_rut = str(fall_2022["Rut Guía"][i]).replace(".0", "")
            teacher2_rut = str(fall_2022["Rut Co-Guía I"][i]).replace(".0", "")
            teacher3_rut = str(fall_2022["Rut Co-Guía II"][i]).replace(".0", "")

            ruts = [teacher1_rut, teacher2_rut, teacher3_rut]

            for rut in ruts:
                if rut != "nan":
                    total_ruts[rut] = total_ruts.get(rut, 0) + 1

            print(ruts)

            work_title = fall_2022["Tema"][i]
            print(work_title)
            work_content = fall_2022["Texto Propuesta"][i]

            translated_title = translate_es_en(work_title)
            translated_content = translate_es_en(work_content)

            # Se pasa al extractor y se obtienen las keywords asociadas.
            formatted_input = convert_input_format(translated_title, translated_content)
            # formatted_input = convert_input_format(translated_title, None)
            extractor_output = json.loads(transformation(formatted_input))

            tagged_concepts = extractor_output[0]["tags"]
            scores = extractor_output[0]["scores"]

            self.stdout.write(
                self.style.SUCCESS(
                    f"Conceptos que el extractor pudo inferir del input: \n {tagged_concepts}\n"
                    + f"Scores respectivos: {scores}"
                )
            )

            teachers_courses_rank = teacher_similarity_calculator(
                tagged_concepts, scores, top_n, all_teachers
            )

            print(teachers_courses_rank[0])
            print(teachers_courses_rank[1])

            for teacher in teachers_courses_rank[0].keys():
                teachers_count[teacher] = teachers_count.get(teacher, 0) + 1
                if teacher.rut in ruts:
                    self.stdout.write(
                        self.style.SUCCESS(f"{teacher} dentro de la lista!")
                    )
                    success += 1

            print("\n")

        for i in spring_2022.index:
            teacher1_rut = str(spring_2022["Rut Guía"][i]).replace(".0", "")
            teacher2_rut = str(spring_2022["Rut Co-Guía I"][i]).replace(".0", "")
            teacher3_rut = str(spring_2022["Rut Co-Guía II"][i]).replace(".0", "")

            ruts = [teacher1_rut, teacher2_rut, teacher3_rut]

            print(ruts)

            for rut in ruts:
                if rut != "nan":
                    total_ruts[rut] = total_ruts.get(rut, 0) + 1

            work_title = spring_2022["Tema"][i]
            print(work_title)
            work_content = spring_2022["Texto Propuesta"][i]

            translated_title = translate_es_en(work_title)
            translated_content = translate_es_en(work_content)

            # Se pasa al extractor y se obtienen las keywords asociadas.
            formatted_input = convert_input_format(translated_title, translated_content)
            # formatted_input = convert_input_format(translated_title, None)
            extractor_output = json.loads(transformation(formatted_input))

            tagged_concepts = extractor_output[0]["tags"]
            scores = extractor_output[0]["scores"]

            self.stdout.write(
                self.style.SUCCESS(
                    f"Conceptos que el extractor pudo inferir del input: \n {tagged_concepts}\n"
                    + f"Scores respectivos: {scores}"
                )
            )

            teachers_courses_rank = teacher_similarity_calculator(
                tagged_concepts, scores, top_n, all_teachers
            )

            print(teachers_courses_rank[0])
            print(teachers_courses_rank[1])

            for teacher in teachers_courses_rank[0].keys():
                teachers_count[teacher] = teachers_count.get(teacher, 0) + 1
                if teacher.rut in ruts:
                    self.stdout.write(
                        self.style.SUCCESS(f"{teacher} dentro de la lista!")
                    )
                    success += 1

            print("\n")

        self.stdout.write(
            self.style.WARNING(f"Precision: {success / total_rows * 100}%")
        )

        self.stdout.write(
            self.style.WARNING(
                f"Recall: {success / sum(total_ruts.values()) * 100}% \n"
            )
        )

        sorted_teachers_count = sorted(
            teachers_count.items(), key=lambda x: x[1], reverse=True
        )

        print(f"{sorted_teachers_count} \n")

        end = time.process_time()

        print(f"Tiempo del test: {datetime.timedelta(seconds=(end-start))} \n")
