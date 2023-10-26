# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

from django.core.management.base import BaseCommand, CommandParser
from teachers.models import Teacher, OpenAlexWork, TeacherWorkKeyword
from teachers.teacher_data_extraction.ucampus_api import (
    get_person_info,
)


class Command(BaseCommand):
    help = "Llamado a la API de U-Campus para extraer los cursos dictados y tesis/memorias donde han participado"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        teachers = Teacher.objects.all()
        for teacher in teachers:
            try:
                # Ahora se obtendrán los trabajos a partir de la url.
                teacher_works = get_person_info(teacher.rut)

                self.stdout.write(
                    self.style.SUCCESS(f"Respuesta de la API exitosa. Ahora ...\n")
                )

                # Es una lista con los resultados.
                # El abstract viene en formato de índice invertido.
                for result in teacher_works:
                    pass

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al momento de guardar datos provenientes de U-Campus para {teacher.name}: "
                        + format(exc)
                    )
                )
