from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

helsinki_es_en = "Helsinki-NLP/opus-mt-es-en"

model_es_en = AutoModelForSeq2SeqLM.from_pretrained(helsinki_es_en)
tokenizer_es_en = AutoTokenizer.from_pretrained(helsinki_es_en)


def translate_es_en(text_input):
    encoded_input = tokenizer_es_en.encode(
        text_input, return_tensors="pt", padding=True, truncation=True
    )
    translated_tokens = model_es_en.generate(encoded_input)
    translated_text = tokenizer_es_en.decode(
        translated_tokens[0], skip_special_tokens=True
    )

    return translated_text


helsinki_en_es = "Helsinki-NLP/opus-mt-en-es"

model_en_es = AutoModelForSeq2SeqLM.from_pretrained(helsinki_en_es)
tokenizer_en_es = AutoTokenizer.from_pretrained(helsinki_en_es)


def translate_en_es(text_input):
    encoded_input = tokenizer_en_es.encode(
        text_input, return_tensors="pt", padding=True, truncation=True
    )
    translated_tokens = model_en_es.generate(encoded_input)
    translated_text = tokenizer_en_es.decode(
        translated_tokens[0], skip_special_tokens=True
    )

    return translated_text
