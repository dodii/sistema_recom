import json
import pandas as pd
import time
import datetime
from teachers.models import Teacher
from django.core.management.base import BaseCommand
from teachers.transformers.translation_download import translate_es_en

from teachers.transformers.embeddings_download import (
    teacher_similarity_calculator,
)

from teachers.openalex_extractor.extractor_script import (
    convert_input_format,
    transformation,
)


class Command(BaseCommand):
    help = "Test de accuracy con datos históricos de memorias y guías/co-guías"

    def handle(self, *args, **options):

        start = time.process_time()

        oa_teachers = Teacher.objects.exclude(openalex_id="")
        all_teachers = Teacher.objects.all()

        top_n_teachers = 5

        fall_2022 = pd.read_excel("informes_e/datos_otono_2022_keywords_gpt.xlsx")
        spring_2022 = pd.read_excel("informes_e/datos_primavera_2022_keywords_gpt.xlsx")

        total_rows = len(fall_2022) + len(spring_2022)

        success = 0

        total_ruts = {}

        for i in fall_2022.index:
            teacher1_rut = str(fall_2022["Rut Guía"][i]).replace(".0", "")
            teacher2_rut = str(fall_2022["Rut Co-Guía I"][i]).replace(".0", "")
            teacher3_rut = str(fall_2022["Rut Co-Guía II"][i]).replace(".0", "")

            ruts = [teacher1_rut, teacher2_rut, teacher3_rut]

            # Para el recall
            for rut in ruts:
                if rut != "nan":
                    total_ruts[rut] = total_ruts.get(rut, 0) + 1

            print(ruts)

            work_title = fall_2022["Tema"][i]
            print(work_title)
            # work_content = fall_2022["Texto Propuesta"]

            translated_title = translate_es_en(work_title)
            # translated_content = translate_es_en(work_content)

            # Se pasa al extractor y se obtienen las keywords asociadas.
            formatted_input = convert_input_format(translated_title)
            extractor_output = json.loads(transformation(formatted_input))

            tagged_concepts = extractor_output[0]["tags"]
            scores = extractor_output[0]["scores"]

            self.stdout.write(
                self.style.SUCCESS(
                    f"Conceptos que el extractor pudo inferir del input: \n {tagged_concepts}\n"
                    + f"Scores respectivos: {scores}"
                )
            )

            # teachers_rank = teacher_similarity_calculator(
            #     tagged_concepts, scores, top_n_teachers, oa_teachers
            # )
            teachers_rank = teacher_similarity_calculator(
                tagged_concepts, scores, top_n_teachers, all_teachers
            )

            # print(teachers_rank)

            for teacher in teachers_rank.keys():
                if teacher.rut in ruts:
                    self.stdout.write(
                        self.style.SUCCESS(f"{teacher} dentro de la lista! \n")
                    )
                    success += 1

        self.stdout.write(
            self.style.WARNING(f"Precision: {success / len(fall_2022) * 100}%")
        )

        self.stdout.write(
            self.style.WARNING(
                f"Precision / 5: {success / (len(fall_2022)*top_n_teachers) * 100}%"
            )
        )

        self.stdout.write(
            self.style.WARNING(f"Recall: {success / sum(total_ruts.values()) * 100}%")
        )

        # for i in spring_2022.index:
        #     teacher1_rut = str(spring_2022["Rut Guía"][i]).replace(".0", "")
        #     teacher2_rut = str(spring_2022["Rut Co-Guía I"][i]).replace(".0", "")
        #     teacher3_rut = str(spring_2022["Rut Co-Guía II"][i]).replace(".0", "")

        #     ruts = [teacher1_rut, teacher2_rut, teacher3_rut]

        #     print(ruts)

        #     work_title = spring_2022["Tema"][i]
        #     print(work_title)
        #     # work_content = spring_2022["Texto Propuesta"]

        #     translated_title = translate_es_en(work_title)
        #     # translated_content = translate_es_en(work_content)

        #     # Se pasa al extractor y se obtienen las keywords asociadas.
        #     formatted_input = convert_input_format(translated_title)
        #     extractor_output = json.loads(transformation(formatted_input))

        #     tagged_concepts = extractor_output[0]["tags"]
        #     scores = extractor_output[0]["scores"]

        #     self.stdout.write(
        #         self.style.SUCCESS(
        #             f"Conceptos que el extractor pudo inferir del input: \n {tagged_concepts}\n"
        #             + f"Scores respectivos: {scores}"
        #         )
        #     )

        #     teachers_rank = teacher_similarity_calculator(
        #         tagged_concepts, scores, top_n_teachers, all_teachers
        #     )

        #     print(teachers_rank)

        #     for teacher in teachers_rank.keys():
        #         if teacher.rut in ruts:
        #             self.stdout.write(
        #                 self.style.SUCCESS(f"{teacher} dentro de la lista!")
        #             )
        #             success += 1

        #     print("\n")

        # print(f"{success / len(spring_2022) * 100}% de aciertos")

        # print(f"{success / total_rows * 100}% de aciertos")

        end = time.process_time()

        print(f"Tiempo del test: {datetime.timedelta(seconds=(end-start))}")
