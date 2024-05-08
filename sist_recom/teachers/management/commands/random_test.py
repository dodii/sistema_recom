import random
import pandas as pd
import time
import datetime
from statistics import mean, stdev
from django.core.management.base import BaseCommand
from teachers.models import Teacher


class Command(BaseCommand):
    help = "Test con recomendaciones aleatorias"

    def handle(self, *args, **options):

        start = time.process_time()

        topn = 7

        # all_teachers = list(Teacher.objects.all())
        all_teachers = list(Teacher.objects.exclude(openalex_id=""))

        test_results = []

        # contar docentes que fueron recomendados por este sistema.
        teachers_count = {}
        for teacher in all_teachers:
            teachers_count[teacher] = 0

        fall_2022 = pd.read_excel("informes_e/datos_otono_2022_keywords_gpt.xlsx")
        spring_2022 = pd.read_excel("informes_e/datos_primavera_2022_keywords_gpt.xlsx")

        total_rows = len(fall_2022) + len(spring_2022)

        for i in range(1, 100):

            success = 0

            total_ruts = {}

            for i in fall_2022.index:
                teacher1_rut = str(fall_2022["Rut Guía"][i]).replace(".0", "")
                teacher2_rut = str(fall_2022["Rut Co-Guía I"][i]).replace(".0", "")
                teacher3_rut = str(fall_2022["Rut Co-Guía II"][i]).replace(".0", "")

                ruts = [teacher1_rut, teacher2_rut, teacher3_rut]

                for rut in ruts:
                    if rut != "nan":
                        total_ruts[rut] = total_ruts.get(rut, 0) + 1

                topn_random_teachers = random.sample(all_teachers, topn)

                for teacher in topn_random_teachers:
                    teachers_count[teacher] = teachers_count.get(teacher, 0) + 1
                    if teacher.rut in ruts:
                        success += 1

            for i in spring_2022.index:
                teacher1_rut = str(spring_2022["Rut Guía"][i]).replace(".0", "")
                teacher2_rut = str(spring_2022["Rut Co-Guía I"][i]).replace(".0", "")
                teacher3_rut = str(spring_2022["Rut Co-Guía II"][i]).replace(".0", "")

                ruts = [teacher1_rut, teacher2_rut, teacher3_rut]

                for rut in ruts:
                    if rut != "nan":
                        total_ruts[rut] = total_ruts.get(rut, 0) + 1

                topn_random_teachers = random.sample(all_teachers, topn)

                for teacher in topn_random_teachers:
                    teachers_count[teacher] = teachers_count.get(teacher, 0) + 1
                    if teacher.rut in ruts:
                        success += 1

            test_results.append(success / total_rows * 100)

        end = time.process_time()

        print(f"Tiempo del test: {datetime.timedelta(seconds=(end-start))} \n")

        print(
            f"{len(teachers_count)} teachers: {teachers_count} \navg {mean(teachers_count.values())} \nstd dev {stdev(teachers_count.values())} \n"
        )

        print(
            f"test results: Acc promedio: {mean(test_results)} \ndesv estandar: {stdev(test_results)}"
        )
