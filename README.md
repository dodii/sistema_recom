# Sistema de recomendación para evaluar memorias en el DCC

Está construido sobre Django y PostgreSQL, junto a la extensión [pgvector](https://github.com/pgvector/pgvector-python) para almacenar vectores de word embeddings generados por el modelo multilenguaje [
paraphrase-multilingual-mpnet-base-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2) de [Sentence Transformers](https://huggingface.co/sentence-transformers).

Utiliza el [modelo V2 de extracción de conceptos de OpenAlex](https://github.com/ourresearch/openalex-concept-tagging/tree/main) con [Tensorflow](https://www.tensorflow.org/install/pip?hl=es).


