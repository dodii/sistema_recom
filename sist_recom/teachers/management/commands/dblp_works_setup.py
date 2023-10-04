# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

from django.core.management.base import BaseCommand
from teachers.models import Teacher, DBLPWork
from teachers.teacher_data_extraction.academic_repository import (
    get_dblp_works,
)


class Command(BaseCommand):
    help = "Llamado a la API de DBLP para extraer los trabajos de los docentes que tengan perfil en este sitio"

    def handle(self, *args, **options):
        # Hacemos query a la tabla que contiene los docentes en la DB.
        # Deben tener id en dblp. Los que no tienen, venían con el string vacío
        # desde el repositorio.
        teachers = Teacher.objects.exclude(dblp_id="")
        for teacher in teachers:
            try:
                # Esto devuelve la lista [{'article': ...}], donde estan todos los
                # trabajos: artículos, proceedings, etc., relacionados con el investigador.
                teacher_works = get_dblp_works(teacher.dblp_id)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Respuesta de DBLP exitosa. Ahora guardando trabajos de {teacher.name} en la base de datos: \n"
                    )
                )

                for work in teacher_works:
                    # Voy a revisar el trabajo como un diccionario porque de partida no sé
                    # si es "article", "inproceedings", etc.
                    for key in work:
                        self.stdout.write(
                            self.style.SUCCESS(str((work[key]["title"])) + "\n")
                        )

                        dblp_work = DBLPWork(
                            title=work[key]["title"],
                            teacher=teacher,
                            year=work[key]["year"],
                        )
                        dblp_work.save()

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al momento de guardar datos provenientes de DBLP para {teacher.name}: "
                        + format(exc)
                    )
                )
