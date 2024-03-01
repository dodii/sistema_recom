from collections import defaultdict
from django.core.management.base import BaseCommand
from teachers.models import (
    Keyword,
    Teacher,
    FCFMCourse,
    GuidedThesis,
    TeacherKeywordRelationship,
    GuidedThesisKeywordRelationship,
    FCFMCourseKeywordRelationship,
)
from teachers.transformers.embeddings_download import (
    get_embeddings_of_model,
)


class Command(BaseCommand):
    help = "Complemento final de keywords para docentes en base a sus cursos y tesis/memorias guiadas"
    "o co-guiadas. Esto es para docentes que no tienen keywords provenientes de OpenAlex (porque no"
    "tienen datos en el sitio)."

    def handle(self, *args, **options):
        teachers = Teacher.objects.filter(openalex_id="")
        print(teachers)

        for teacher in teachers:
            associated_thesis = GuidedThesis.objects.filter(teacher=teacher)
            associated_courses = FCFMCourse.objects.filter(teacher=teacher)
            total_thesis = associated_thesis.count()
            total_courses = associated_courses.count()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Docente: {teacher} \nMemorias/tesis: {total_thesis} \nCursos: {total_courses} \n"
                )
            )

            keywords_frequency = defaultdict(int)
            scores_list = defaultdict(list)
            score_aggregator = defaultdict(float)

            for thesis in associated_thesis:
                keywords = GuidedThesisKeywordRelationship.objects.filter(
                    guided_thesis=thesis
                )

                for kw in keywords:
                    keywords_frequency[kw.keyword] += 1
                    scores_list[kw.keyword].append(kw.score)  # type: ignore
                    score_aggregator[kw.keyword] += kw.score  # type: ignore

            for course in associated_courses:
                keywords = FCFMCourseKeywordRelationship.objects.filter(
                    fcfm_course=course
                )

                for kw in keywords:
                    keywords_frequency[kw.keyword] += 1
                    scores_list[kw.keyword].append(kw.score)  # type: ignore
                    score_aggregator[kw.keyword] += kw.score  # type: ignore

            sorted_kw_fr = sorted(
                keywords_frequency.items(), key=lambda x: x[1], reverse=True
            )

            final_scores = {
                keyword: score_aggregator[keyword] / keywords_frequency[keyword]
                for keyword, _ in sorted_kw_fr
            }

            inverse_frequency = {
                keyword: 1 / keywords_frequency[keyword]
                for keyword in keywords_frequency
            }

            penalized_final_scores = {
                keyword: normalized_score * (1 - inverse_frequency[keyword])
                for keyword, normalized_score in final_scores.items()
            }

            purged_dict = {
                keyword: score
                for keyword, score in penalized_final_scores.items()
                if score > 0
            }

            sorted_purged_dict = sorted(
                purged_dict.items(), key=lambda x: x[1], reverse=True
            )

            # Multiplicamos los scores por 100 para que se asemejen en dimensiones
            # a los provenientes de OpenAlex.
            final_dict = list(
                map(lambda x: (x[0], round(x[1] * 100, 1)), sorted_purged_dict)
            )

            print(final_dict)

            # Finalmente, asociamos las keywords al perfil del docente con los
            # nuevos scores que acabamos de calcular.
            for tuple in final_dict:
                keyword = Keyword.objects.get(keyword=tuple[0])

                # Solamente se crea la nueva relación, porque las keywords ya existen
                # al haber sido extraídas de sus cursos/tesis para calcular todo esto.
                try:
                    teacher_kw_relationship = TeacherKeywordRelationship(
                        teacher=teacher,
                        keyword=keyword,
                        score=tuple[1],
                    )
                    teacher_kw_relationship.save()

                except Exception as exc:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error al añadir '{keyword.keyword}' a docente '{teacher.name}': "
                            + format(exc)
                            + "\n"
                        )
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Se añadieron {len(sorted_purged_dict)} keywords a docente {teacher} \n"
                )
            )
