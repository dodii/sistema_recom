# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

from django.core.management.base import BaseCommand, CommandParser
from teachers.models import Teacher, OpenAlexWork
from teachers.teacher_data_extraction.academic_works_apis import (
    get_openalex_works_of_teacher,
)
from teachers.teacher_data_extraction.utils import inverted_index_abstract_to_plain_text


class Command(BaseCommand):
    help = "Llamado a la API de OpenAlex para extraer los trabajos de los docentes que tengan perfil en este sitio"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        # Se extraen los datos de los trabajos para cada docente con información en OpenAlex.
        teachers = Teacher.objects.filter(openalex_works_url__isnull=False)
        for teacher in teachers:
            try:
                # Ahora se obtendrán los trabajos a partir de la url.
                teacher_works = get_openalex_works_of_teacher(
                    teacher.openalex_works_url
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Respuesta de la API exitosa. Ahora se guardarán \
                        {teacher_works['meta']['count']} trabajo(s) de {teacher.name} en la base de datos. \n"
                    )
                )

                # Es una lista con los resultados.
                # El abstract viene en formato de índice invertido.
                for result in teacher_works["results"]:
                    work = OpenAlexWork(
                        title=result["title"],
                        teacher=teacher,
                        year=result["publication_year"],
                        abstract=inverted_index_abstract_to_plain_text(
                            result["abstract_inverted_index"]
                        ),
                        openalex_concepts=[
                            r["display_name"] for r in result["concepts"]
                        ],
                    )

                    work.save()

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al momento de guardar datos provenientes de OpenAlex para {teacher.name}: "
                        + format(exc)
                    )
                )
