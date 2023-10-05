from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

helsinki_translation_model = "Helsinki-NLP/opus-mt-es-en"

model = AutoModelForSeq2SeqLM.from_pretrained(helsinki_translation_model)
tokenizer = AutoTokenizer.from_pretrained(helsinki_translation_model)


def translate_text(text_input):
    encoded_input = tokenizer.encode(
        text_input, return_tensors="pt", padding=True, truncation=True
    )
    translated_tokens = model.generate(encoded_input)
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

    return translated_text
