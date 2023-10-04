from sentence_transformers import SentenceTransformer

paraph_multiling = "paraphrase-multilingual-mpnet-base-v2"

model = SentenceTransformer(paraph_multiling)


def get_embeddings_of_model(list_of_keywords):
    embeddings = model.encode(list_of_keywords)

    # Por ahora es solo esto.

    return embeddings
