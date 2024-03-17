# Sistema de recomendación para evaluar memorias en el DCC

Está construido sobre Django y PostgreSQL, junto a la extensión [pgvector](https://github.com/pgvector/pgvector-python) para almacenar vectores de word embeddings generados por el modelo multilenguaje [
paraphrase-multilingual-mpnet-base-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2) de [Sentence Transformers](https://huggingface.co/sentence-transformers).

Utiliza el [modelo V2 de extracción de conceptos de OpenAlex](https://github.com/ourresearch/openalex-concept-tagging/tree/main) con [Tensorflow](https://www.tensorflow.org/install/pip?hl=es).

Este modelo puede ser descargado desde AWS, como describe su repositorio. El resto de elementos se descarga a través de Python.

Fueron creados [comandos personalizables](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/) de Django para ejecutar llamados a las distintas APIs que poblan la base de datos. 
