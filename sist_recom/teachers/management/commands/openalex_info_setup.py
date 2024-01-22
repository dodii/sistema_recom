from django.core.management.base import BaseCommand, CommandParser
from teachers.models import (
    Teacher,
    Keyword,
    TeacherKeywordRelationship,
    ScholarWork,
    ScholarWorkKeywordRelationship,
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
        # Los que no tienen ID de OpenAlex no recibirán información de vuelta desde la API.
        teachers = Teacher.objects.exclude(openalex_id="")

        self.stdout.write(
            self.style.SUCCESS(
                f"Añadiendo keywords del perfil de OpenAlex de cada docente a la base de datos local. \n"
            )
        )

        for teacher in teachers:
            try:
                # Las keywords de su perfil.
                teacher_keywords = get_openalex_teacher_data(teacher.openalex_id)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Respuesta de la API exitosa. Añadiendo keywords de {teacher.name}... \n"
                    )
                )

                for concept in teacher_keywords["x_concepts"]:
                    # Como los conceptos vienen de OpenAlex, su
                    # display_name es único (excepto que algunos vienen
                    # con mayúsculas, así que las pasaré todas a lowercase).
                    lowercase_kw = concept["display_name"].lower()

                    # Si la keyword es nueva en la base de datos, se guarda.
                    # Esto devuelve tupla (objeto, flag)
                    keyword = Keyword.objects.get_or_create(
                        keyword=lowercase_kw,
                        embedding=get_embeddings_of_model(lowercase_kw),
                    )

                    # Se crea la nueva relación
                    teacher_kw_relationship = TeacherKeywordRelationship(
                        teacher=teacher,
                        keyword=keyword[0],
                        score=concept["score"],
                    )
                    teacher_kw_relationship.save()

                # Ahora se obtendrán los trabajos a partir de la url.
                teacher_works = get_openalex_works_of_teacher(
                    teacher.openalex_works_url
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Respuesta de la API exitosa. Guardando {teacher_works['meta']['count']} "
                        + f"trabajos (máx. primeros 200) de {teacher.name} en la base de datos... \n"
                    )
                )

                # Es una lista con los resultados.
                for result in teacher_works["results"]:
                    # Vemos si el trabajo ya existe en nuestra base de datos.
                    # Esto devuelve tupla (objeto, flag)
                    scholar_work = ScholarWork.objects.get_or_create(
                        openalex_id=result["id"],
                        title=result["title"],
                        year=result["publication_year"],
                        embedding_name=get_embeddings_of_model(result["title"]),
                        abstract=inverted_index_abstract_to_plain_text(
                            result["abstract_inverted_index"]
                        ),
                        doi=result["doi"],
                    )

                    scholar_work[0].teacher.add(teacher)

                    # Ahora se añaden las keywords al trabajo.
                    for concept in result["concepts"]:
                        # Se guarda keyword si resulta ser nueva en la base de datos.
                        # Se calcula su embedding.
                        # Se pasa a lowercase por lo antes mencionado
                        lowercase_kw = concept["display_name"].lower()
                        keyword = Keyword.objects.get_or_create(
                            keyword=lowercase_kw,
                            get_embeddings_of_model=get_embeddings_of_model(
                                lowercase_kw
                            ),
                        )

                        work_kw_relationship = ScholarWorkKeywordRelationship(
                            scholar_work=scholar_work[0],
                            keyword=keyword,
                            score=concept["score"],
                        )
                        work_kw_relationship.save()

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al momento de guardar datos provenientes de OpenAlex para {teacher.name}: "
                        + format(exc)
                        + "\n"
                    )
                )
