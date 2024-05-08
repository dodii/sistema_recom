# Sistema de recomendación para evaluar memorias en el DCC

Está construido con Django y PostgreSQL, junto a la extensión [pgvector](https://github.com/pgvector/pgvector-python) para almacenar vectores de word embeddings generados por el modelo multilenguaje [paraphrase multilingual mpnet base v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2) de [Sentence Transformers](https://huggingface.co/sentence-transformers).

Este proyecto utiliza el [modelo V2 de extracción de conceptos de OpenAlex](https://github.com/ourresearch/openalex-concept-tagging/tree/main) con [Tensorflow](https://www.tensorflow.org/install/pip?hl=es) para etiquetar con keywords las publicaciones, cursos, memorias guiadas, etc., que estén asociada a docentes. Luego, el modelo mpnet se encarga de crear los embeddings de estas palabras claves. 

El modelo V2 puede ser descargado desde AWS, como describe su repositorio. Debe ser colocado y descomprimido dentro de sist_recom/teachers/openalex_extractor/model_files. El resto de elementos se descarga con Python dentro del proyecto mismo al ejecutar código.

Fueron creados [comandos personalizables](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/) de Django para ejecutar llamados a las distintas APIs que poblan la base de datos y configuran otros aspectos. 

Para correr estos scripts, basta con ejecutar *python manage.py [script.py]* en sist_recom/, donde script.py es el nombre del script, por ejemplo *random_test.py*.

Una vez creada la base de datos con Postgres y activado pgvector en ella, el orden de ejecución de los scripts es:

1. *teachers_list_setup.py*: Se guarda el plantel completo de docentes disponibles del DCC en la base de datos desde U-Campus y leyendo el json local con información adicional de docentes (id de OpenAlex y docentes PEX). La API de U-Campus solamente acepta llamadas desde una IP conocida, se debe conversar con la ADI o con U-Campus para gestionar eso, en caso de necesitarlo.

Desde su API no se puede rescatar un grupo con docentes PEX, deben ser buscados individualmente. Por eso están guardados en un json aparte, actualizado hasta enero 2024.

2. *transformers_setup.py*: Descarga de los modelos desde HuggingFace. Modelo de traducción y embeddings. El de traducción español-inglés es esencial para el modelo V2 de OpenAlex, funciona mucho mejor en inglés que en español (a pesar de indicar que funciona en varios idiomas).

3. *openalex_info_setup.py*: Se llama a la API de OpenAlex para extraer las publicaciones académicas de los docentes, almacenando estos trabajos en la base de datos. 

4. *ucampus_courses_thesis_setup.py*: Llamada a API de
U-Campus para extraer cursos dictadps y memorias/tesis guiadas por cada docente del departamento.

5. *courses_thesis_kw_setup.py*: Etiquetado de keywords
con modelo V2 para los datos provenientes del script anterior.

6. *final_keywords_setup.py*: 