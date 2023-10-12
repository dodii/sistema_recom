import json
from django.core.management.base import BaseCommand, CommandParser
from teachers.models import Teacher, TeacherKeyword
from teachers.teacher_data_extraction.academic_works_apis import (
    get_openalex_teacher_data,
)
from teachers.transformers.embeddings_download import get_embeddings_of_model


class Command(BaseCommand):
    help = "Lectura del json local que contiene las ID correctas de OpenAlex de los docentes del DCC."

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        teachers = Teacher.objects.all()

        with open("openalex_teachers_id.json") as f:
            ids_data = json.load(f)

        for teacher in teachers:
            try:
                teacher_id = ids_data[teacher.name]["oa_id"]
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Asignando los datos de OpenAlex a {teacher.name}"
                    )
                )
                teacher.openalex_id = teacher_id

                # También le asignamos la url de su trabajo.
                teacher.openalex_works_url = ids_data[teacher.name]["works_api_url"]

                # Y las keywords del perfil su perfil en OpenAlex.
                teacher_data = get_openalex_teacher_data(teacher_id)

                for concept in teacher_data["x_concepts"]:
                    # Se filtran keywords que potencialmente estorben
                    if concept["score"] > 0:
                        # Si la keyword es nueva en la base de datos, se guarda
                        if not TeacherKeyword.objects.filter(
                            keyword=concept["display_name"]
                        ).exists():
                            keyword = TeacherKeyword(keyword=concept["display_name"])

                            keyword.save()
                            keyword.teacher.add(teacher)

                        # Si la keyword ya existe
                        else:
                            keyword = TeacherKeyword.objects.get(
                                keyword=concept["display_name"]
                            )
                            keyword.teacher.add(teacher)

                teacher.save()

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al momento de guardar datos de {teacher.name}: "
                        + format(exc)
                    )
                )
