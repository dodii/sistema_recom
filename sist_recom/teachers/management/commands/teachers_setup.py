# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

from django.core.management.base import BaseCommand
from teachers.models import Teacher
from teachers.teacher_data_extraction.academic_repository import (
    make_request_to_repository_api,
)


class Command(BaseCommand):
    help = "Llamado a la API del repositorio de docentes para poblar la base de datos del sistema de recomendación."

    def handle(self, *args, **options):
        try:
            teachers_dictionary = make_request_to_repository_api()
            self.stdout.write(
                self.style.SUCCESS(
                    "Respuesta de la API exitosa. Procediendo a guardar a los docentes en la base de datos:"
                )
            )

            for teacher_id in teachers_dictionary:
                # Revisamos si ya está en la base de datos guardado.
                # En caso de que queramos actualizar la lista.
                if not Teacher.objects.filter(repository_id=teacher_id):
                    teacher_data = teachers_dictionary[teacher_id]
                    self.stdout.write(self.style.SUCCESS(teacher_data))

                    teacher = Teacher(
                        repository_id=teacher_id,
                        dblp_id=teacher_data.get("dblp_id", None),
                        name=teacher_data["nombre"],
                        external_name=teacher_data.get("nombre_externo", None),
                    )
                    teacher.save()

        except Exception as exc:
            self.stdout.write(
                self.style.ERROR(
                    "Error al momento de guardar datos provenientes de la API: "
                    + format(exc)
                )
            )
