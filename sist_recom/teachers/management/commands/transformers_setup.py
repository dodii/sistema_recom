import runpy
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Descarga del modelo de traducción y word embeddings desde HuggingFace. Quedarán en el caché."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "Se descargarán los modelos de traducción español-inglés"
            )
        )
        try:
            runpy.run_path(path_name="./teachers/transformers/translation_download.py")

            self.stdout.write(
                self.style.SUCCESS(
                    "Los modelos de traducción español-inglés se han descargado y guardado con éxito. \n"
                )
            )

            self.stdout.write(
                self.style.SUCCESS("Se descargará el modelo de embeddings")
            )
            runpy.run_path(path_name="./teachers/transformers/embeddings_download.py")

            self.stdout.write(
                self.style.SUCCESS(
                    "El modelo de embeddings se ha descargado y guardado con éxito."
                )
            )

        except Exception as exc:
            self.stdout.write(
                self.style.ERROR(
                    "Error al momento de descargar los modelos desde Huggingface: "
                    + format(exc)
                )
            )
