import runpy
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Configuración del modelo de extracción de conceptos de OpenAlex."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Configuración del extractor de conceptos")
        )
        try:
            runpy.run_path(
                path_name="./teachers/openalex_extractor/extractor_script.py"
            )

        except Exception as exc:
            self.stdout.write(
                self.style.ERROR(
                    "Error al momento de configurar el extractor: " + format(exc)
                )
            )
