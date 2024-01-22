from scipy import spatial
from itertools import islice
from django.db.models import Avg
from pgvector.django import CosineDistance
from teachers.models import (
    Teacher,
    Keyword,
    FCFMCourse,
    GuidedThesis,
    ScholarWork,
)
from sentence_transformers import SentenceTransformer

paraph_multiling = "paraphrase-multilingual-mpnet-base-v2"

# El modelo debería quedar en el caché para su posterior reutilización.
model = SentenceTransformer(paraph_multiling)


def get_embeddings_of_model(list_of_keywords):
    embeddings = model.encode(list_of_keywords)

    # Por ahora es solo esto.
    return embeddings


# En esta primera instancia, simplemente tomaré las keywords más
# cercanas y entregaré una lista con los profes indicados.
def teacher_similarity_calculator(string, top_n_keywords, top_n_teachers):
    teachers = Teacher.objects.all()
    ranking = {}
    embedding = get_embeddings_of_model(string)

    for teacher in teachers:
        teacher_profile_kw = teacher.keyword

        selected_kw = teacher_profile_kw.order_by(
            CosineDistance("embedding", embedding)
        )[:top_n_keywords]

        # Obtengo la distancia.
        try:
            # print(f"Keywords más parecidas: {selected_kw[0].keyword}")

            # Embedding promedio de las top_n_keywords.
            avg_embedding = selected_kw.aggregate(Avg("embedding"))

            # distance = selected_kw.annotate(  # type: ignore
            #     distance=CosineDistance("embedding", avg_embedding["embedding__avg"])
            # )
            distance = spatial.distance.cosine(
                embedding, avg_embedding["embedding__avg"]
            )

            # ranking[teacher] = [distance[0].distance, selected_kw]  # type: ignore
            ranking[teacher] = [distance, selected_kw]

        except Exception as exc:
            print(
                f"{teacher.name} aún no tiene keywords que lo caractericen. "
                # + f"Excepción en particular: {exc}\n"
            )

    # Distancia Coseno va entre 0 y 2.
    # Distancia Coseno = 1 - Simiitud Coseno
    # Mientras más cercano a 0, mayor la similitud semántica.
    # Entrega lista ordenada ascendentemente con los items del diccionario.
    sorted_teacher_ranking = sorted(ranking.items(), key=lambda x: x[1][0])

    return dict(islice(sorted_teacher_ranking, top_n_teachers))


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
