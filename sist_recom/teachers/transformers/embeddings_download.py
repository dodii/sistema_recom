from pgvector.django import CosineDistance
from teachers.models import TeacherKeyword
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
def teacher_similarity_calculator(embedding, top_n):
    selected_kw = TeacherKeyword.objects.order_by(
        CosineDistance("embedding", embedding)
    )[:top_n]

    return selected_kw


def scholarworks_similarity_calculator(embedding):
    pass


def guidedthesis_similarity_calculator(embedding):
    pass


def fcfmcourses_similarity_calculator(embedding):
    pass
