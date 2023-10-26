# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

from django.core.management.base import BaseCommand, CommandParser
from teachers.models import Teacher, OpenAlexWork, TeacherWorkKeyword
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
        teachers = Teacher.objects.exclude(openalex_id="")
        for teacher in teachers:
            try:
                # Ahora se obtendrán los trabajos a partir de la url.
                teacher_works = get_openalex_works_of_teacher(
                    teacher.openalex_works_url
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Respuesta de la API exitosa. Ahora se guardarán {teacher_works['meta']['count']} trabajo(s) de {teacher.name} en la base de datos. \n"
                    )
                )

                # Es una lista con los resultados.
                # El abstract viene en formato de índice invertido.
                for result in teacher_works["results"]:
                    # Vemos si el trabajo ya existe en nuestra base de datos
                    if not OpenAlexWork.objects.filter(
                        openalex_id=result["id"]
                    ).exists():
                        work = OpenAlexWork(
                            title=result["title"],
                            year=result["publication_year"],
                            doi=result["doi"],
                            openalex_id=result["id"],
                            abstract=inverted_index_abstract_to_plain_text(
                                result["abstract_inverted_index"]
                            ),
                        )

                        work.save()
                        work.teacher.add(teacher)

                    # Si ya existe, simplemente asignamos el trabajo al docente.
                    else:
                        work = OpenAlexWork.objects.get(openalex_id=result["id"])
                        work.teacher.add(teacher)

                    # Ahora se añaden las keywords al trabajo.
                    # Solamente si el score es mayor a 20.
                    # Como los conceptos vienen de OpenAlex, su
                    # display_name es único.
                    for concept in result["concepts"]:
                        # Volvemos a tomar el trabajo ya guardado en la base de datos.
                        work = OpenAlexWork.objects.get(openalex_id=result["id"])

                        # Se filtran keywords que potencialmente estorben
                        if concept["score"] > 0.2:
                            # Si la keyword es nueva en la base de datos, se guarda
                            if not TeacherWorkKeyword.objects.filter(
                                keyword=concept["display_name"]
                            ).exists():
                                keyword = TeacherWorkKeyword(
                                    keyword=concept["display_name"]
                                )

                                keyword.save()
                                keyword.associated_work.add(work)

                            # Si la keyword ya existe
                            else:
                                keyword = TeacherWorkKeyword.objects.get(
                                    keyword=concept["display_name"]
                                )
                                keyword.associated_work.add(work)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Añadidas las keywords de los trabajo(s) de {teacher.name} \n"
                    )
                )

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al momento de guardar datos provenientes de OpenAlex para {teacher.name}: "
                        + format(exc)
                    )
                )
