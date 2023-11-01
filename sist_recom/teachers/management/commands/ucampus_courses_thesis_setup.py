# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

from django.core.management.base import BaseCommand, CommandParser
from teachers.models import Teacher, TeacherCourse, GuidedThesis
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
                    self.style.SUCCESS(
                        f"Respuesta de la API exitosa. Revisando memorias/tesis y cursos de {teacher.name} \n"
                    )
                )

                for result in teacher_works:
                    data_result = teacher_works[result]
                    if data_result["tipo"] == "cursos_dictados":
                        # Si ya existe, solo añadimos el profe al curso
                        if TeacherCourse.objects.filter(
                            course_code=data_result["codigo"]
                        ):
                            course = TeacherCourse.objects.get(
                                course_code=data_result["codigo"]
                            )
                            course.teacher.add(teacher)

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Curso {data_result['codigo']} {data_result['nombre']} ya existe, añadiendo solamente docente \n"
                                )
                            )

                        # De lo contrario, creamos todo
                        else:
                            course = TeacherCourse(
                                title=data_result["nombre"],
                                year=data_result["anno"],
                                course_code=data_result["codigo"],
                            )
                            course.save()
                            course.teacher.add(teacher)

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Curso {data_result['codigo']} {data_result['nombre']} creado \n"
                                )
                            )

                    elif data_result["tipo"] == "memorias" and (
                        data_result["participacion"] == "Profesor Guía"
                        or data_result["participacion"] == "Profesor Co-guía"
                    ):
                        if GuidedThesis.objects.filter(ucampus_id=result):
                            work = GuidedThesis.objects.get(ucampus_id=result)
                            work.teacher.add(teacher)
                        else:
                            work = GuidedThesis(
                                title=data_result["titulo"],
                                year=data_result["anno"],
                                ucampus_id=result,
                            )
                            work.save()
                            work.teacher.add(teacher)

                        self.stdout.write(
                            self.style.SUCCESS(f"Memoria/tesis {work.title} \n")
                        )

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al momento de guardar datos provenientes de U-Campus para {teacher.name}: "
                        + format(exc)
                    )
                )
