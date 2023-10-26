# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

import json
from django.core.management.base import BaseCommand
from teachers.teacher_data_extraction.academic_works_apis import (
    get_openalex_teacher_data,
)
from teachers.models import Teacher, TeacherKeyword
from teachers.teacher_data_extraction.academic_repository import (
    make_request_to_repository_api,
)


class Command(BaseCommand):
    help = "Llamado a la API del repositorio de docentes, OpenAlex y U-Campus para poblar la base de datos del sistema de recomendación."

    def handle(self, *args, **options):
        # Aquí están las URL de los trabajos de los docentes en OpenAlex.
        # Están guardadas en un json porque la búsqueda y match de cada
        # docente con su perfil correcto (desambiguado) fue realizado a mano.
        with open("openalex_teachers_id.json") as f:
            ids_rut_data = json.load(f)

        try:
            teachers_dictionary = make_request_to_repository_api()
            self.stdout.write(
                self.style.SUCCESS(
                    "Respuesta de la API del repositorio exitosa. Procediendo a guardar docentes en la base de datos: \n"
                )
            )

            for teacher_id in teachers_dictionary:
                # Revisamos si ya está en la base de datos guardado.
                # En caso de que queramos actualizar la lista.
                if not Teacher.objects.filter(repository_id=teacher_id):
                    teacher_data = teachers_dictionary[teacher_id]

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Guardando datos desde el repositorio a {teacher_data['nombre']}"
                        )
                    )
                    teacher = Teacher(
                        repository_id=teacher_id,
                        name=teacher_data["nombre"],
                        external_name=teacher_data.get("nombre_externo", ""),
                    )

                    # Lectura del JSON de datos para la ID de openalex, la URL de sus trabajos
                    # y el RUT.
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Asignando RUT y datos de OpenAlex a {teacher.name} \n"
                        )
                    )
                    teacher.rut = ids_rut_data[teacher_data["nombre"]]["rut"]
                    teacher.openalex_id = ids_rut_data[teacher_data["nombre"]]["oa_id"]
                    teacher.openalex_works_url = ids_rut_data[teacher_data["nombre"]][
                        "works_api_url"
                    ]

                    teacher.save()

                    # Y las keywords del perfil su perfil en OpenAlex, en caso de tener
                    # información en esa plataforma.
                    if teacher.openalex_id != "":
                        teacher_openalex_data = get_openalex_teacher_data(
                            teacher.openalex_id
                        )

                        for concept in teacher_openalex_data["x_concepts"]:
                            # Se filtran keywords que potencialmente estorben.
                            # Como los conceptos vienen de OpenAlex, su
                            # display_name es único.
                            if concept["score"] > 20:
                                # Si la keyword es nueva en la base de datos, se guarda
                                if not TeacherKeyword.objects.filter(
                                    keyword=concept["display_name"]
                                ).exists():
                                    keyword = TeacherKeyword(
                                        keyword=concept["display_name"]
                                    )

                                    keyword.save()
                                    keyword.teacher.add(teacher)

                                # Si la keyword ya existe
                                else:
                                    keyword = TeacherKeyword.objects.get(
                                        keyword=concept["display_name"]
                                    )
                                    keyword.teacher.add(teacher)

                        teacher.save()

        except Exception as exc:
            self.stdout.write(
                self.style.ERROR("Error al momento de guardar datos: " + format(exc))
            )
