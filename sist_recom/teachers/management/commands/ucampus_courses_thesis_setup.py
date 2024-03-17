from django.core.management.base import BaseCommand, CommandParser
from teachers.models import Teacher, FCFMCourse, GuidedThesis
from teachers.teacher_data_extraction.ucampus_api import (
    get_person_info,
)
from sist_recom.teachers.transformers.embeddings_and_filtering import (
    get_embeddings_of_model,
)


class Command(BaseCommand):
    help = (
        "Llamado a la API de U-Campus para extraer los cursos dictados y tesis/memorias donde han participado. "
        "Este script puede tardar en comenzar su ejecución unos minutos al comienzo porque carga el modelo de embeddings."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f"Añadiendo cursos y tesis/memorias de docentes desde U-Campus \n"
            )
        )

        # La lista completa de docentes que se almacenan en la base de datos de esta aplicación.
        teachers = Teacher.objects.all()

        for teacher in teachers:
            try:
                # Ahora se obtendrán los trabajos a partir de la url.
                teacher_works = get_person_info(teacher.rut)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Respuesta de U-Campus exitosa. Revisando memorias/tesis y cursos de {teacher.rut}: {teacher.name} \n"
                    )
                )

                for result in teacher_works:
                    data_result = teacher_works[result]
                    if data_result["tipo"] == "cursos_dictados":
                        # Si ya existe, solo añadimos el profe al curso
                        if FCFMCourse.objects.filter(course_code=data_result["codigo"]):
                            course = FCFMCourse.objects.get(
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
                            course = FCFMCourse(
                                title=data_result["nombre"],
                                year=data_result["anno"],
                                course_code=data_result["codigo"],
                                embedding_name=get_embeddings_of_model(
                                    data_result["nombre"]
                                ),
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
                                embedding_name=get_embeddings_of_model(
                                    data_result["titulo"]
                                ),
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
                        + "\n"
                    )
                )
