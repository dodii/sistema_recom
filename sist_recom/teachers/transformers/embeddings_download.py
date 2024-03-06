from scipy import spatial
from statistics import mean
import numpy as np
from collections import defaultdict
from itertools import islice
from django.db.models import Avg
from pgvector.django import CosineDistance
from teachers.models import (
    Teacher,
    Keyword,
    TeacherKeywordRelationship,
    FCFMCourse,
    FCFMCourseKeywordRelationship,
    GuidedThesis,
    ScholarWork,
)
from sentence_transformers import SentenceTransformer

paraph_multiling = "paraphrase-multilingual-mpnet-base-v2"

# El modelo debería quedar en el caché para su posterior reutilización.
model = SentenceTransformer(paraph_multiling, cache_folder="teachers/transformers/")


def get_embeddings_of_model(list_of_keywords):
    embeddings = model.encode(list_of_keywords)

    # Por ahora es solo esto.
    return embeddings


def teacher_similarity_calculator(
    concepts_list, concepts_scores, top_n_teachers, teachers_list
):
    # teachers = Teacher.objects.all()
    # teachers = Teacher.objects.exclude(openalex_id="")
    teachers_ranking = {}

    for teacher in teachers_list:
        teacher_keywords = teacher.keyword.all()

        # Casos de docentes sin keywords
        # no pueden ser recomendados, así que
        # serán omitidos.
        if len(teacher_keywords) == 0:
            continue

        # print(teacher)

        results_dict = {}

        for i, concept in enumerate(concepts_list):
            concept_score = concepts_scores[i]
            input_concept_emb = get_embeddings_of_model(concept)

            distances = []

            for keyword in teacher_keywords:
                # similitud coseno = 1 - distancia coseno
                distance = 1 - spatial.distance.cosine(
                    input_concept_emb, keyword.embedding
                )  # type: ignore

                teacher_kw_relationship = TeacherKeywordRelationship.objects.get(
                    teacher=teacher, keyword=keyword
                )
                # pondered_distance = distance * teacher_kw_relationship.score  # type: ignore
                pondered_distance = distance  # ignorar score keyword-docente por ahora

                # distances.append(r)
                distances.append((keyword.keyword, pondered_distance))

            # results_list.append(result)

            distances.sort(key=lambda x: x[1], reverse=True)

            # Progresion geometrica: pondera en mayor cantidad la
            # keyword con mayor semejanza, disminuyendo exponencialmente
            # a medida que bajamos por la lista ordenada
            pondered_distances = {
                x: x[1] * (concept_score ** (i - 1)) for i, x in enumerate(distances)
            }

            results_dict[concept] = max(pondered_distances, key=pondered_distances.get)  # type: ignore

            # Para peobar con min max, sumare todo nomas
            # results_dict[concept] = sum(pondered_distances)  # type: ignore

            # # Lista normalizacion
            # pondered_distances = [
            #     x[1] * (concept_score ** (i - 1))
            #     for i, x in enumerate(distances, start=1)
            # ]

            # results_dict[concept] = sum(pondered_distances) / len(teacher_keywords)

        # # normalizacion
        # total_score = sum(results_dict.values()) / len(teacher_keywords)
        # kw_list = [results_dict[x] for x in results_dict]

        # keyword maxima
        total_score = sum([results_dict[x][1] for x in results_dict])
        kw_list = [results_dict[x][0] for x in results_dict]
        teachers_ranking[teacher] = (kw_list, total_score)

        # teachers_ranking[teacher] = (
        #     max(results_dict, key=results_dict.get),  # type: ignore
        #     max(results_dict.values()),
        # )

    # # # min max scaling
    # lambda_f = lambda x: (
    #     (x - min(teachers_ranking.values()))
    #     / (max(teachers_ranking.values()) - min(teachers_ranking.values()))
    # )

    # normalized_rankings = {
    #     k: lambda_f(teachers_ranking[k]) for k in teachers_ranking.keys()
    # }

    sorted_teacher_ranking = sorted(
        teachers_ranking.items(), key=lambda x: x[1][1], reverse=True
    )

    return dict(islice(sorted_teacher_ranking, top_n_teachers))


def teacher_ranking_keywords_approach(concepts_list, concepts_scores, top_n_teachers):
    concepts_calculation_dict = {}

    for i, concept in enumerate(concepts_list):
        concept_score = concepts_scores[i]
        input_concept_emb = get_embeddings_of_model(concept)

        # nearest neighbors keywords
        # Cosine Distance = 1 - Similitud Coseno
        # 0 = iguales, 1 = sin correlacion, 2 = opuestos
        # ordena de más similar a opuesto
        distances = Keyword.objects.annotate(
            distance=1 - CosineDistance("embedding", input_concept_emb)
        ).order_by("-distance")

        pondered_distances = {}
        for i, x in enumerate(distances):
            result = x.distance * (concept_score ** (i - 1))  # type: ignore
            if result > 0:  # Rescatamos relaciones relevantes nomás
                # Las palabras que más se parecen tendrán más valor. A medida que disminuye el parecido,
                # la ponderación disminuye siguiendo esta progresión geométrica.
                # De esta forma, las keywords menos relevantes valen mucho menos.
                pondered_distances[x] = (x.distance) * concept_score ** (i - 1)  # type: ignore

        concepts_calculation_dict[concept] = pondered_distances

    related_teachers = {}
    related_courses = defaultdict(list)

    for concept, related_concepts in concepts_calculation_dict.items():
        for kw, score in related_concepts.items():
            teacher_relationships = TeacherKeywordRelationship.objects.filter(
                keyword=kw
            )
            if teacher_relationships:
                for relationship in teacher_relationships:
                    related_teachers[relationship.teacher] = (
                        related_teachers.get(relationship.teacher, 0)
                        + score * relationship.score
                        # if relationship.teacher.openalex_id
                        # != ""  # Para testear sin docentes con keywords generadas por las memorias, para evitar cruce de datos.
                        # else 0
                    )

            # related_courses_relationships = (
            #     FCFMCourseKeywordRelationship.objects.filter(keyword=kw)
            # )
            # if related_courses_relationships:
            #     for relationship in related_courses_relationships:
            #         course = relationship.fcfm_course
            #         teachers = course.teacher.all()
            #         for teacher in teachers:
            #             related_courses[teacher].append((course, relationship.score))
            #         # related_courses[relationship.fcfm_course] = (
            #         #     related_courses.get(relationship.fcfm_course, 0)
            #         #     + score * relationship.score
            #         # )

    # Sumamos ponderación de cursos si es que tienen
    # for teacher, courses_scores_list in related_courses.items():
    #     avg_sum = mean([duple[1] for duple in courses_scores_list])
    #     related_teachers[teacher] = related_teachers.get(teacher, 0) + avg_sum

    # # min max scaling
    lambda_f = lambda x: (
        (x - min(related_teachers.values()))
        / (max(related_teachers.values()) - min(related_teachers.values()))
    )

    normalized_rankings = {
        k: lambda_f(related_teachers[k]) for k in related_teachers.keys()
    }

    sorted_teacher_ranking = sorted(
        normalized_rankings.items(), key=lambda x: x[1], reverse=True
    )

    top_n_result = dict(islice(sorted_teacher_ranking, top_n_teachers))

    top_n_courses = [
        # {teacher: related_courses[teacher][:top_n_teachers]} for teacher in top_n_result
    ]

    return [top_n_result, top_n_courses]


def scholarworks_similarity_calculator(teacher, top_n_works, keywords):
    publications = ScholarWork.objects.filter(teacher=teacher)
    avg_embedding = keywords.aggregate(Avg("embedding"))["embedding__avg"]

    # Obtengo la distancia.
    try:
        # Por ahora solo con el embedding del nombre del curso.
        selected_works = publications.order_by(
            CosineDistance("embedding_name", avg_embedding)
        )[:top_n_works]

        return selected_works
    except Exception:
        print(
            f"{teacher.name} aún no tiene publicaciones guardadas, se omite su cálculo. \n"
        )


def guidedthesis_similarity_calculator(teacher, top_n_thesis, keywords):  # string):
    courses = GuidedThesis.objects.filter(teacher=teacher)
    avg_embedding = keywords.aggregate(Avg("embedding"))["embedding__avg"]

    # Obtengo la distancia.
    try:
        # Por ahora solo con el embedding del nombre del curso.
        selected_thesis = courses.order_by(
            CosineDistance("embedding_name", avg_embedding)
        )[:top_n_thesis]

        return selected_thesis
    except Exception:
        print(
            f"{teacher.name} aún no tiene tesis/memorias guiadas, se omite su cálculo. \n"
        )


def fcfmcourses_similarity_calculator(teacher, top_n_cursos, keywords):  # string):
    courses = FCFMCourse.objects.filter(teacher=teacher)
    avg_embedding = keywords.aggregate(Avg("embedding"))["embedding__avg"]

    # Obtengo la distancia.
    try:
        # Por ahora solo con el embedding del nombre del curso.
        selected_courses = courses.order_by(
            CosineDistance("embedding_name", avg_embedding)
        )[:top_n_cursos]

        return selected_courses
    except Exception:
        print(f"{teacher.name} aún no tiene cursos, se omite su cálculo. \n")
