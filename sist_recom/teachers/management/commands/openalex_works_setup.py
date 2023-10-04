# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

from django.core.management.base import BaseCommand
from teachers.models import Teacher, DBLPWork
from teachers.teacher_data_extraction.academic_works_apis import (
    get_openalex_teacher_data,
    get_openalex_works_of_teacher,
)


class Command(BaseCommand):
    help = (
        "Llamado a la API de OpenAlex para extraer los trabajos de los docentes que tengan perfil en este sitio \n"
        "Es importante notar que algunos docentes no están OpenAlex. A su vez, la API no siempre devuelve al docente que "
        "queremos, así que hay un proceso manual posterior a este donde se corrigen errores para asignar la id correcta."
    )

    def handle(self, *args, **options):
        # Primero se obtendrá el id de OpenAlex para los investigadores/docentes del DCC.
        teachers = Teacher.objects.all()
        for teacher in teachers:
            try:
                # Se tomará el primero en la lista, que es el de mayor relevance score
                openalex_data = get_openalex_teacher_data(teacher.name)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Respuesta de la API exitosa. Ahora se guardará la id de {teacher.name} en la base de datos: \n \n"
                        + f"{openalex_data['results'][0]['id']} \n"
                        + f"{openalex_data['results'][0]['works_api_url']} \n"
                    )
                )

                teacher.openalex_id = openalex_data["results"][0]["id"]
                teacher.openalex_works_url = openalex_data["results"][0][
                    "works_api_url"
                ]
                teacher.save(update_fields=["openalex_id", "openalex_works_url"])

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al momento de guardar datos provenientes de OpenAlex para {teacher.name}: "
                        + format(exc)
                    )
                )
