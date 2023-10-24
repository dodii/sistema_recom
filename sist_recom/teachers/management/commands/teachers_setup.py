# Llamada a la API del repositorio para poblar la base de datos
# con los docentes actuales.

import json
from django.core.management.base import BaseCommand
from sist_recom.teachers.teacher_data_extraction.academic_works_apis import (
    get_openalex_teacher_data,
)
from teachers.models import Teacher, TeacherKeyword
from teachers.teacher_data_extraction.academic_repository import (
    make_request_to_repository_api,
)


class Command(BaseCommand):
    help = "Llamado a la API del repositorio de docentes y OpenAlex para poblar la base de datos del sistema de recomendación."

    def handle(self, *args, **options):
        with open("openalex_teachers_id.json") as f:
            ids_data = json.load(f)

        with open("docentes_dcc.json") as f:
            dcc_ucampus_data = json.load(f)

        try:
            teachers_dictionary = make_request_to_repository_api()
            self.stdout.write(
                self.style.SUCCESS(
                    "Respuesta de la API del repositorio exitosa. Procediendo a guardar a los docentes en la base de datos:"
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
                        name=teacher_data["nombre"],
                        external_name=teacher_data.get("nombre_externo", ""),
                        rut=teacher_data["rut"]
                    )

                    # Lectura del JSON de datos
                    teacher_id = ids_data[teacher_data["nombre"]]["oa_id"]
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Asignando los datos de OpenAlex a {teacher_data['nombre']}"
                        )
                    )
                    teacher.openalex_id = teacher_id

                    teacher.openalex_works_url = ids_data[teacher_data["nombre"]][
                        "works_api_url"
                    ]

                    teacher.save()

                    # Y las keywords del perfil su perfil en OpenAlex.
                    teacher_data = get_openalex_teacher_data(teacher_id)

                    for concept in teacher_data["x_concepts"]:
                        # Se filtran keywords que potencialmente estorben
                        if concept["score"] > 0:
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

                    # Ahora el rut los docentes de jornada completa y parcial, 
                    # como identificador adicional para poder
                    # trabajar con los datos de U-Campus
                    teacher.rut = 

        except Exception as exc:
            self.stdout.write(
                self.style.ERROR(
                    "Error al momento de guardar datos del docente: " + format(exc)
                )
            )
