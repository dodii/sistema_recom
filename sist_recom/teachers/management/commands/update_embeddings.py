from django.core.management.base import BaseCommand
from teachers.models import GuidedThesis
from teachers.transformers.embeddings_download import get_embeddings_of_model


class Command(BaseCommand):
    help = "Completar embeddings faltantes en Guided Thesis, que por alguna razón están vacíos."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Añadiendo embeddings faltantes."))

        guided_thesis = GuidedThesis.objects.filter(embedding_name__isnull=True)

        for thesis in guided_thesis:
            embedding = get_embeddings_of_model(thesis.title)

            thesis.embedding_name = embedding
            thesis.save(update_fields=["embedding_name"])
