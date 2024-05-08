import wordcloud
from itertools import islice
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter, defaultdict
from django.core.management.base import BaseCommand
from teachers.models import (
    Keyword,
    FCFMCourse,
    GuidedThesis,
    ScholarWork,
    FCFMCourseKeywordRelationship,
    GuidedThesisKeywordRelationship,
    ScholarWorkKeywordRelationship,
    Teacher,
    TeacherKeywordRelationship,
)


class Command(BaseCommand):

    def handle(self, *args, **options):

        # papers_concepts = defaultdict(int)

        # total_papers = len(ScholarWork.objects.all())
        # print(total_papers)

        # for paper in ScholarWork.objects.all():
        #     related_kw = paper.keyword.all()  # type: ignore
        #     for kw in related_kw:
        #         papers_concepts[kw.keyword] += 1

        # sorted_papers_concepts = dict(
        #     sorted(papers_concepts.items(), key=lambda item: item[1], reverse=True)
        # )

        # print(papers_concepts)

        # teacher_concepts = {}

        # for teacher in Teacher.objects.all():
        #     related_kw = teacher.keyword.all()  # type: ignore
        #     for kw in related_kw:
        #         relation = TeacherKeywordRelationship.objects.get(
        #             teacher=teacher, keyword=kw
        #         )
        #         print(relation)
        #         teacher_concepts[kw.keyword] = (
        #             (
        #                 teacher_concepts[kw.keyword][0] + 1,
        #                 teacher_concepts[kw.keyword][1] + relation.score,
        #             )
        #             if kw.keyword in teacher_concepts.keys()
        #             else (1, relation.score)
        #         )

        # sorted_teacher_concepts = dict(
        #     sorted(teacher_concepts.items(), key=lambda item: item[1][1], reverse=True)
        # )

        # first30_teacher_concepts = {
        #     k: (sorted_teacher_concepts[k][0], sorted_teacher_concepts[k][1])
        #     for k in list(sorted_teacher_concepts)[:30]
        # }

        # print(first30_teacher_concepts)

        # thesis_concepts = defaultdict(int)

        # total_thesis = len(GuidedThesis.objects.all())

        # for thesis in GuidedThesis.objects.all():
        #     related_kw = thesis.keyword.all()  # type: ignore
        #     for kw in related_kw:
        #         thesis_concepts[kw.keyword] += 1

        # sorted_thesis_concepts = dict(
        #     sorted(thesis_concepts.items(), key=lambda item: item[1], reverse=True)
        # )

        # first10_concepts = {
        #     k: sorted_thesis_concepts[k] for k in list(sorted_thesis_concepts)[:10]
        # }
        # print(first10_concepts)

        courses_concepts = defaultdict(int)

        total_courses = len(FCFMCourse.objects.all())

        for course in FCFMCourse.objects.all():
            related_kw = course.keyword.all()  # type: ignore
            for kw in related_kw:
                courses_concepts[kw.keyword] += 1

        sorted_courses_concepts = dict(
            sorted(courses_concepts.items(), key=lambda item: item[1], reverse=True)
        )

        first10_concepts = {
            k: sorted_courses_concepts[k] for k in list(sorted_courses_concepts)[:10]
        }
        print(first10_concepts)

        # wc = wordcloud.WordCloud(
        #     width=800, height=800, max_words=30
        # ).generate_from_frequencies(frequencies=teacher_concepts, max_font_size=None)

        # plt.figure(figsize=(20, 10), facecolor="k")
        # plt.imshow(wc, interpolation="bilinear")
        # plt.axis("off")
        # plt.tight_layout(pad=0)
        # plt.savefig("wc_teachers.png", format="png")
        # plt.clf()

        # first10_concepts = {
        #     k: sorted_papers_concepts[k] / total_papers * 100
        #     for k in list(sorted_papers_concepts)[:10]
        # }
        # print(first10_concepts)

        # Plot histogram
        plt.figure(figsize=(17, 17))
        plt.bar(
            list(first10_concepts.keys()),
            [x[1] for x in first10_concepts.items()],
        )
        plt.xlabel("Concepto")
        plt.ylabel("Apariciones")
        plt.title("Top 10 conceptos más recurrentes en cursos dictados")
        plt.xticks(range(10), rotation=45)
        # plt.xticks(np.arange(min(counts), max(counts), step=5))
        # plt.yticks(range(int(max(list(first10_concepts.values())) + 1)))
        # plt.grid(axis="y", alpha=0.5)
        plt.savefig("top10conceptos_cursos.png")
        plt.clf()
