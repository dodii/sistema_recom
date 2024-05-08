from scipy import spatial
import numpy as np
from itertools import islice
from django.db.models import Avg
from pgvector.django import CosineDistance
from teachers.models import (
    Keyword,
    TeacherKeywordRelationship,
    FCFMCourse,
    GuidedThesis,
    ScholarWork,
)
from sentence_transformers import SentenceTransformer

paraph_multiling = "paraphrase-multilingual-mpnet-base-v2"

# El modelo debería quedar en el caché para reutilizarlo.
model = SentenceTransformer(paraph_multiling, cache_folder="teachers/transformers/")


def get_embeddings_of_model(list_of_keywords):
    embeddings = model.encode(list_of_keywords)
    return embeddings


# obsoleto
def teacher_similarity_calculator(
    concepts_list, concepts_scores, top_n_teachers, teachers_list
):
    teachers_ranking = {}

    for teacher in teachers_list:
        teacher_keywords = teacher.keyword.all()

        # Casos de docentes sin keywords
        # no pueden ser recomendados, así que
        # serán omitidos.
        if len(teacher_keywords) == 0:
            continue

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
                pondered_distance = distance * teacher_kw_relationship.score  # type: ignore
                # pondered_distance = distance  # ignorar score keyword-docente por ahora

                distances.append((keyword.keyword, pondered_distance))

            distances.sort(key=lambda x: x[1], reverse=True)

            # Progresion geometrica: pondera en mayor cantidad la
            # keyword con mayor semejanza, disminuyendo exponencialmente
            # a medida que bajamos por la lista ordenada
            pondered_distances = {
                x: x[1] * (concept_score ** (i - 1)) for i, x in enumerate(distances)
            }

            results_dict[concept] = max(pondered_distances, key=pondered_distances.get)  # type: ignore

            # Para probar con min max, sumare todo nomas
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


def teacher_ranking_keywords_approach(
    concepts_list, concepts_scores, top_n_teachers=7, test_flag=False
):
    concepts_calculation_dict = {}

    for i, concept in enumerate(concepts_list):
        concept_score = concepts_scores[i]
        input_concept_emb = get_embeddings_of_model(concept)

        # Nearest neighbors keywords
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
                pondered_distances[x] = result  # type: ignore

        concepts_calculation_dict[concept] = pondered_distances

    related_teachers = {}

    for concept, related_concepts in concepts_calculation_dict.items():
        for kw, score in related_concepts.items():
            teacher_relationships = TeacherKeywordRelationship.objects.filter(
                keyword=kw
            )
            if teacher_relationships:
                for relationship in teacher_relationships:
                    related_teachers[relationship.teacher] = (
                        0
                        if (
                            test_flag == True and relationship.teacher.openalex_id == ""
                        )
                        else related_teachers.get(relationship.teacher, 0)
                        + score * relationship.score
                    )

    # min max scaling
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

    ranking = dict(islice(sorted_teacher_ranking, top_n_teachers))

    # Consultar publicaciones, memorias guiadas y cursos.
    top_n_works = get_most_related_works(ranking, concepts_list)

    return [ranking, top_n_works]


def get_most_related_works(teachers_ranking, input_concepts, top_n_works=5):

    # avg embedding
    avg_input_embedding = np.add.reduce(
        [get_embeddings_of_model(concept) for concept in input_concepts]
    ) / len(input_concepts)

    teacher_works = {}

    for teacher in teachers_ranking:
        works = {}
        works.update(
            {
                course: (
                    course.keyword.all().aggregate(Avg("embedding"))["embedding__avg"]
                    if course.keyword.all()
                    else course.embedding_name
                )
                for course in FCFMCourse.objects.filter(teacher=teacher)
            }
        )
        works.update(
            {
                publication: (
                    publication.keyword.all().aggregate(Avg("embedding"))[
                        "embedding__avg"
                    ]
                    if publication.keyword.all()
                    else publication.embedding_name
                )
                for publication in ScholarWork.objects.filter(teacher=teacher)
            }
        )
        works.update(
            {
                thesis: (
                    thesis.keyword.all().aggregate(Avg("embedding"))["embedding__avg"]
                    if thesis.keyword.all()
                    else thesis.embedding_name
                )
                for thesis in GuidedThesis.objects.filter(teacher=teacher)
            }
        )

        for work, avg_embedding in works.items():
            try:
                works[work] = 1 - spatial.distance.cosine(
                    avg_embedding, avg_input_embedding
                )  # type: ignore
            except Exception as exc:
                print(exc)

        sorted_works = sorted(works.items(), key=lambda x: x[1], reverse=True)
        teacher_works[teacher] = dict(islice(sorted_works, top_n_works))

    return teacher_works
