# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

from django.core.management.base import BaseCommand, CommandParser
from teachers.models import (
    Teacher,
    TeacherKeyword,
    OpenAlexScholarWork,
    TeacherScholarWorkKeyword,
)
from teachers.teacher_data_extraction.academic_works_apis import (
    get_openalex_works_of_teacher,
    get_openalex_teacher_data,
)
from teachers.teacher_data_extraction.utils import inverted_index_abstract_to_plain_text
from teachers.transformers.embeddings_download import get_embeddings_of_model


class Command(BaseCommand):
    help = "Llamado a la API de OpenAlex para extraer las keywords y trabajos de docentes que tengan perfil"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        # Se extraen los datos de los trabajos para cada docente con información en OpenAlex.
        # Se excluyen los que no tienen perfil en OpenAlex.
        teachers = Teacher.objects.exclude(openalex_id="")

        self.stdout.write(
            self.style.SUCCESS(
                f"Añadiendo keywords del perfil de cada docente a la base de datos. \n"
            )
        )

        for teacher in teachers:
            try:
                # Las keywords de su perfil.
                teacher_keywords = get_openalex_teacher_data(teacher.openalex_id)

                if teacher.openalex_id != "":
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Respuesta de la API exitosa. Añadiendo keywords de {teacher.name}... \n"
                        )
                    )

                    for concept in teacher_keywords["x_concepts"]:
                        # Se filtran keywords que potencialmente estorben.
                        # Como los conceptos vienen de OpenAlex, su
                        # display_name es único.
                        if concept["score"] > 20:
                            # Si la keyword es nueva en la base de datos, se guarda
                            if not TeacherKeyword.objects.filter(
                                keyword=concept["display_name"]
                            ).exists():
                                keyword = TeacherKeyword(
                                    keyword=concept["display_name"],
                                    embedding=get_embeddings_of_model(
                                        concept["display_name"]
                                    ),
                                )

                                keyword.save()
                                keyword.teacher.add(teacher)

                            # Si la keyword ya existe, se le añade a la persona.
                            else:
                                keyword = TeacherKeyword.objects.get(
                                    keyword=concept["display_name"]
                                )
                                keyword.teacher.add(teacher)

                        teacher.save()

                # Ahora se obtendrán los trabajos a partir de la url.
                teacher_works = get_openalex_works_of_teacher(
                    teacher.openalex_works_url
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Respuesta de la API exitosa. Guardando {teacher_works['meta']['count']} trabajo(s) (máx. primeros 200) de {teacher.name} en la base de datos. \n"
                    )
                )

                # Es una lista con los resultados.
                # El abstract viene en formato de índice invertido.
                for result in teacher_works["results"]:
                    # Vemos si el trabajo ya existe en nuestra base de datos
                    if not OpenAlexScholarWork.objects.filter(
                        openalex_id=result["id"]
                    ).exists():
                        work = OpenAlexScholarWork(
                            title=result["title"],
                            year=result["publication_year"],
                            embedding_name=get_embeddings_of_model(result["title"]),
                            openalex_id=result["id"],
                            abstract=inverted_index_abstract_to_plain_text(
                                result["abstract_inverted_index"]
                            ),
                            doi=result["doi"],
                        )

                        work.save()
                        work.teacher.add(teacher)

                    # Si ya existe, simplemente asignamos el trabajo al docente.
                    else:
                        work = OpenAlexScholarWork.objects.get(openalex_id=result["id"])
                        work.teacher.add(teacher)

                    # Ahora se añaden las keywords al trabajo.
                    # Solamente si el score es mayor a 50.
                    # Como los conceptos vienen de OpenAlex, su
                    # display_name es único.
                    for concept in result["concepts"]:
                        # Volvemos a tomar el trabajo ya guardado en la base de datos.
                        work = OpenAlexScholarWork.objects.get(openalex_id=result["id"])

                        # Se filtran keywords que potencialmente estorben
                        if concept["score"] > 0.5:
                            # Se guarda keyword si resulta ser nueva en la base de datos.
                            # Se calcula su embedding.
                            if not TeacherScholarWorkKeyword.objects.filter(
                                keyword=concept["display_name"]
                            ).exists():
                                keyword = TeacherScholarWorkKeyword(
                                    keyword=concept["display_name"],
                                    embedding=get_embeddings_of_model(
                                        concept["display_name"]
                                    ),
                                )

                                keyword.save()
                                keyword.associated_work.add(work)

                            # En caso de que la keyword ya exista
                            else:
                                keyword = TeacherScholarWorkKeyword.objects.get(
                                    keyword=concept["display_name"]
                                )
                                keyword.associated_work.add(work)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Añadidas keywords de trabajo(s) de {teacher.name} \n"
                    )
                )

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al momento de guardar datos provenientes de OpenAlex para {teacher.name}: "
                        + format(exc)
                    )
                )
