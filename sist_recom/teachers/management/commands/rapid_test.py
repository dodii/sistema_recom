from django.core.management.base import BaseCommand
from teachers.models import Teacher


class Command(BaseCommand):
    help = "Adición de conjunto de keywords a cursos y memorias/tesis."

    def handle(self, *args, **options):
        print(len(Teacher.objects.exclude(openalex_id="")))
