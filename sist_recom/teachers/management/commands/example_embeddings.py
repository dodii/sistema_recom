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
        first_emb = get_embeddings_of_model("QuickSort")
        second_emb = get_embeddings_of_model("Complejidad de Algoritmos")
        third_emb = get_embeddings_of_model("Árbol binario")
        fourth_emb = get_embeddings_of_model("Matemáticas")

        result_one = teacher_similarity_calculator(first_emb, 3)
        result_two = teacher_similarity_calculator(second_emb, 3)
        result_three = teacher_similarity_calculator(third_emb, 3)
        result_four = teacher_similarity_calculator(fourth_emb, 3)

        results = [result_one, result_two, result_three, result_four]

        for queryset in results:
            # [teacher.name for teacher in obj.teacher.all()]
            self.stdout.write(self.style.SUCCESS(str(r.keyword)))
            self.stdout.write(self.style.SUCCESS(str(r.teacher.all())))
