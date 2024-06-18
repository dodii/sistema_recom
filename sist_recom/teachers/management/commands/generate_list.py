from django.core.management.base import BaseCommand

import pandas as pd
from teachers.utils.input_processing import extract_input_keywords, get_profile_keywords
from teachers.transformers.translation_model import translate_es_en
from teachers.transformers.embeddings_and_filtering import (
    teacher_ranking_keywords_approach,
)


class Command(BaseCommand):
    help = "Generación lista recomendación"

    def add_arguments(self, parser):
        parser.add_argument("xlsx_file_path", type=str, help="xlsx file path")
        parser.add_argument("title_column_name", type=str, help="title column name")
        parser.add_argument("summary_column_name", type=str, help="summary column name")

    def handle(self, *args, **options):
        xlsx_file_path = options["xlsx_file_path"]
        if not xlsx_file_path.endswith(".xlsx"):
            self.stdout.write('archivo "%s" no es xlsx' % xlsx_file_path)
            return
        elif not options["title_column_name"] or not options["summary_column_name"]:
            self.stdout.write("falta nombre de la columna titulo o resumen")

        with open(xlsx_file_path, "rb") as xlsx_file:
            df = pd.read_excel(xlsx_file)  # type: ignore
            df = df.fillna("")

            output_list = []

            for row in df.itertuples():
                title = getattr(row, options["title_column_name"])
                summary = getattr(row, options["summary_column_name"])

                keywords_result, scores = extract_input_keywords(title, summary)
                teachers = teacher_ranking_keywords_approach(
                    keywords_result, scores, top_n_teachers=7
                )

                print(teachers[0])

                output_list.append(
                    {
                        "title": title,
                        "abstract": summary,
                        "recommendation": [teacher.name for teacher in teachers[0]],
                    }
                )

            new_df = pd.DataFrame(output_list)
            new_df.to_excel(f"excel_testing/output.xlsx")
