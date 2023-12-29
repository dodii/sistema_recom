from django.core.management.base import BaseCommand, CommandParser
from teachers.models import Teacher, TeacherKeyword
from teachers.transformers.embeddings_download import (
    get_embeddings_of_model,
    teacher_similarity_calculator,
)


class Command(BaseCommand):
    help = "Intentos primera prueba"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        input_embedd = get_embeddings_of_model(
            "Sistema de geolocalización por cercanía a redes wifi"
        )

        # Iterar sobre las keywords de los docentes, si es que tienen.
        # Ver una forma de calcular similitud entre el embedding input y todas
        # estas keywords.

        # Iterar sobre los cursos dictados por los profes, si es que tienen cursos.

        for r in results:
            # [teacher.name for teacher in obj.teacher.all()]
            self.stdout.write(self.style.SUCCESS(str(r.keyword)))
            self.stdout.write(self.style.SUCCESS(str(r.teacher.all())))
