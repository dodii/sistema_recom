from django.core.management.base import BaseCommand, CommandParser
from teachers.models import TeacherKeyword, TeacherWorkKeyword, GuidedThesisKeyword
from teachers.transformers.embeddings_download import get_embeddings_of_model


class Command(BaseCommand):
    help = "Creación de Embeddings de las keywords guardadas."

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        teacher_keywords = TeacherKeyword.objects.all()
        works_keywords = TeacherWorkKeyword.objects.all()
        guided_thesis_keywords = GuidedThesisKeyword.objects.all()

        for keyword in teacher_keywords:
            try:
                if keyword.embedding is None:
                    embedding = get_embeddings_of_model(keyword.keyword)
                    keyword.embedding = embedding
                    keyword.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Generado y guardado embedding para keyword {keyword.keyword}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"El embedding de la keyword {keyword.keyword} ya existe"
                        )
                    )

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error en generación de embeddings de la keyword {keyword.keyword}: "
                        + format(exc)
                    )
                )

        for keyword in works_keywords:
            try:
                if keyword.embedding is None:
                    embedding = get_embeddings_of_model(keyword.keyword)
                    keyword.embedding = embedding
                    keyword.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Generado y guardado embedding para keyword {keyword.keyword}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"El embedding de la keyword {keyword.keyword} ya existe"
                        )
                    )

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error en generación de embeddings de la keyword {keyword.keyword}: "
                        + format(exc)
                    )
                )
        for keyword in guided_thesis_keywords:
            try:
                if keyword.embedding is None:
                    embedding = get_embeddings_of_model(keyword.keyword)
                    keyword.embedding = embedding
                    keyword.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Generado y guardado embedding para keyword {keyword.keyword}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"El embedding de la keyword {keyword.keyword} ya existe"
                        )
                    )

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error en generación de embeddings de la keyword {keyword.keyword}: "
                        + format(exc)
                    )
                )
