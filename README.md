# Sistema de recomendación para evaluar memorias en el DCC

[Repositorio](https://github.com/dodii/sistema_recom)

Está construido con Django y PostgreSQL, junto a la extensión [pgvector](https://github.com/pgvector/pgvector-python) para almacenar vectores de word embeddings generados por el modelo multilenguaje [paraphrase multilingual mpnet base v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2) de [Sentence Transformers](https://huggingface.co/sentence-transformers).

Este proyecto utiliza el [modelo V2 de extracción de conceptos de OpenAlex](https://github.com/ourresearch/openalex-concept-tagging/tree/main) con [Tensorflow](https://www.tensorflow.org/install/pip?hl=es) (2.15) para etiquetar con keywords las publicaciones, cursos, memorias guiadas, etc., que estén asociada a docentes. Luego, el modelo mpnet se encarga de crear los embeddings de estas palabras claves. 

El modelo V2 puede ser descargado desde AWS, como describe su repositorio. Debe ser colocado y descomprimido dentro de sist_recom/teachers/openalex_extractor/model_files. El resto de elementos se descarga con Python dentro del proyecto mismo al ejecutar código.

Fueron creados [comandos personalizables](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/) de Django para ejecutar llamados a las distintas APIs que poblan la base de datos y configuran otros aspectos. 

Para correr estos scripts, basta con ejecutar *python manage.py [script.py]* en sist_recom/, donde script.py es el nombre del script, por ejemplo *random_test.py*.

Una vez creada la base de datos con Postgres y activado pgvector en ella, el orden de ejecución de los scripts es:

1. *teachers_list_setup.py*: Se guarda el plantel completo de docentes disponibles del DCC en la base de datos desde U-Campus y leyendo el json local con información adicional de docentes (id de OpenAlex y docentes PEX). La API de U-Campus solamente acepta llamadas desde una IP conocida, se debe conversar con la ADI o con U-Campus para gestionar eso, en caso de necesitarlo.

Desde su API no se puede rescatar un grupo con docentes PEX, deben ser buscados individualmente. Por eso están guardados en un json aparte, actualizado hasta enero 2024.

2. *transformers_setup.py*: Descarga de los modelos desde HuggingFace. Modelo de traducción y embeddings. El de traducción español-inglés es esencial para el modelo V2 de OpenAlex, funciona mucho mejor en inglés que en español (a pesar de indicar que funciona en varios idiomas). Deberían quedar cacheados.

3. *openalex_info_setup.py*: Se llama a la API de OpenAlex para extraer las publicaciones académicas de los docentes, almacenando estos trabajos en la base de datos. 

4. *ucampus_courses_thesis_setup.py*: Llamada a API de U-Campus para extraer cursos dictadps y memorias/tesis guiadas por cada docente del departamento.

5. *courses_thesis_kw_setup.py*: Etiquetado de keywords con modelo V2 para los datos provenientes del script anterior.

6. *final_keywords_setup.py*: Complemento final de keywords para docentes en base a sus cursos y tesis/memorias guiadas"
    "o co-guiadas. Esto es para docentes que no tienen keywords provenientes de OpenAlex (porque no"
    "tienen datos en el sitio)

Algunos otros scripts son auto explicativos, pero frente a cualquier duda, escribir a r.gonzalezoportot@gmail.com

# IMPORTANTE

Otro script destacado es *generate_list.py*, que toma un archivo excel con columnas que tengan el título y el resumen de un tema de memoria, y devuelve otro archivo excel con las recomendaciones para cada fila.

Se utiliza dando como argumentos el path del archivo y el nombre de las columnas del título y resumen. Si no hay
columna con resumen, por favor crear una dentro del archivo excel de entrada, aunque esté vacía para todas las filas.

Ejemplo de uso: python manage.py generate_list excels/comisiones_ejemplo.xlsx Tema Resumen

En caso de no haber ningún resumen, por favor igual dejar una columna vacía con nombre dentro del archivo de entrada.

El script dejará el archivo en la carpeta excel_testing dentro del proyecto 