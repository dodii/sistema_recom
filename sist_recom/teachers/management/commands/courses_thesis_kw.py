import json
from django.core.management.base import BaseCommand
from teachers.models import (
    Keyword,
    FCFMCourse,
    GuidedThesis,
    FCFMCourseKeywordRelationship,
    GuidedThesisKeywordRelationship,
)
from sist_recom.teachers.transformers.translation_model import translate_es_en
from sist_recom.teachers.transformers.embeddings_and_filtering import (
    get_embeddings_of_model,
)
from teachers.openalex_extractor.extractor_script import (
    convert_input_format,
    transformation,
)


class Command(BaseCommand):
    help = "Adición de conjunto de keywords a cursos y memorias/tesis."

    def handle(self, *args, **options):
        courses = FCFMCourse.objects.all()
        guided_thesis = GuidedThesis.objects.all()

        self.stdout.write(self.style.SUCCESS("Añadiendo keywords a cursos: \n "))

        for course in courses:
            self.stdout.write(
                self.style.SUCCESS(f"{course.course_code} {course.title}")
            )
            output = json.loads(
                transformation(convert_input_format(translate_es_en(course.title)))
            )

            tags = output[0]["tags"]
            scores = output[0]["scores"]

            # Solamente se añaden si tienen un score mayor a 0.3.
            # Esto porque en OpenAlex lo hicieron de esta forma para
            # etiquetar los trabajos de investigación.
            # Se hará lo mismo para mantener la consistencia.
            # Número mágico??!?!?!
            for index, kw in enumerate(tags):
                if scores[index] <= 0.3:
                    break

                lowercase_kw = kw.lower()
                keyword = Keyword.objects.get_or_create(
                    keyword=lowercase_kw,
                    defaults={"embedding": get_embeddings_of_model(lowercase_kw)},
                )

                try:
                    # Creamos la nueva relacion keyword-curso
                    course_kw_relationship = FCFMCourseKeywordRelationship(
                        keyword=keyword[0], fcfm_course=course, score=scores[index]
                    )
                    course_kw_relationship.save()

                    self.stdout.write(self.style.SUCCESS(lowercase_kw))
                except Exception as exc:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error al añadir'{keyword[0].keyword}' a curso '{course.title}': "
                            + format(exc)
                            + "\n"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS("Añadiendo keywords a memorias/tesis: \n ")
        )

        for thesis in guided_thesis:
            self.stdout.write(self.style.SUCCESS(f"{thesis.ucampus_id} {thesis.title}"))
            output = json.loads(
                transformation(convert_input_format(translate_es_en(thesis.title)))
            )

            tags = output[0]["tags"]
            scores = output[0]["scores"]

            # Solamente se añaden si tienen un score mayor a 0.3.
            # Esto porque en OpenAlex lo hicieron de esta forma para
            # etiquetar los trabajos de investigación.
            # Se hará lo mismo para mantener consistencia.
            for index, kw in enumerate(tags):
                if scores[index] < 0.3:
                    break

                lowercase_kw = kw.lower()
                keyword = Keyword.objects.get_or_create(
                    keyword=lowercase_kw,
                    embedding=get_embeddings_of_model(lowercase_kw),
                )

                try:
                    # Creamos la nueva relacion keyword-curso
                    thesis_kw_relationship = GuidedThesisKeywordRelationship(
                        keyword=keyword[0], guided_thesis=thesis, score=scores[index]
                    )
                    thesis_kw_relationship.save()

                    self.stdout.write(self.style.SUCCESS(lowercase_kw))
                except Exception as exc:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error al añadir '{keyword[0].keyword}' a memoria/tesis '{thesis.title}': "
                            + format(exc)
                            + "\n"
                        )
                    )
