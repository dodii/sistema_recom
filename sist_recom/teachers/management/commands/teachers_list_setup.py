import json
from django.core.management.base import BaseCommand, CommandParser
from teachers.models import Teacher
from teachers.teacher_data_extraction.ucampus_api import (
    get_academics_group,
)


class Command(BaseCommand):
    help = "Llamado a la API de U-Campus para extraer docentes. Incluye lectura de info local para complementar el plantel total de docentes."

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        # Docentes jornada completa y parcial. No incluye expertas/os externas/os.
        ucampus_teachers = get_academics_group()

        self.stdout.write(
            self.style.SUCCESS(
                f"Respuesta de U-Campus exitosa. Revisando la lista de docentes jornada completa y parcial. \n"
            )
        )

        # Este json contiene la lista de docentes de jornada completa,
        # parcial y expertas/os externas/os hasta diciembre de 2023.
        # Son los que aparecen en el sitio web del dcc https://www.dcc.uchile.cl/pregrado/academicos/
        with open("openalex_teachers_id.json") as f:
            local_teacher_data = json.load(f)

        for teacher_id in ucampus_teachers:
            try:
                # Guardaremos el/la docente en la base de datos.
                teacher = ucampus_teachers[teacher_id]

                self.stdout.write(
                    self.style.SUCCESS(f"Docente {teacher_id}: {teacher['alias']}")
                )

                # De paso vemos los datos adicionales en el json
                teacher_json = local_teacher_data[teacher["rut"]]

                # El rut es clave primaria, si creo y guardo un docente con un rut que ya existe
                # en la base de datos, Django solamente tratará de actualizarlo.
                new_teacher = Teacher(
                    rut=teacher["rut"],
                    name=teacher["alias"],
                    full_name=teacher["nombre_completo"],
                    openalex_id=teacher_json["oa_id"],
                    openalex_works_url=teacher_json["works_api_url"],
                    dblp_id=teacher_json["dblp_id"],
                )
                new_teacher.save()

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al guardar datos desde U-Campus para {teacher_id}: {ucampus_teachers[teacher_id]['alias']} "
                        + format(exc)
                        + " \n"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "\nRevisando el json local con información de docentes expertos/as externos/as. \n"
            )
        )

        # Ahora iteramos sobre el json local.
        # Se buscarán docentes que no vienen de la request a U-Campus, pero aparecen
        # en el sitio de acádemicos/as del DCC. Recordar que esto sucede con docentes
        # externos/as expertos/as.
        for teacher_rut in local_teacher_data:
            try:
                # Revisamos que no exista.
                if not Teacher.objects.filter(rut=teacher_rut):
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Docente {teacher_rut}: {local_teacher_data[teacher_rut]['alias']}"
                        )
                    )

                    # El rut es clave primaria, si creo y guardo un docente con un rut que ya existe
                    # en la base de datos, Django solamente tratará de actualizarlo.
                    new_teacher = Teacher(
                        rut=teacher_rut,
                        name=local_teacher_data[teacher_rut]["alias"],
                        openalex_id=local_teacher_data[teacher_rut]["oa_id"],
                        openalex_works_url=local_teacher_data[teacher_rut][
                            "works_api_url"
                        ],
                        dblp_id=local_teacher_data[teacher_rut]["dblp_id"],
                    )
                    new_teacher.save()

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error al leer json local para {local_teacher_data[teacher_rut]: {local_teacher_data[teacher_rut]['alias']}} "
                        + format(exc)
                        + " \n"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("Actualización de la lista de docentes completa. \n")
        )
