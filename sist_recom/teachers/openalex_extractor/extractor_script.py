import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import re
import io
import json
import pickle
import pandas as pd
import tensorflow as tf

tf.get_logger().setLevel("ERROR")

###################################################
###
### Este script fue hecho por el equipo de OpenAlex.
### Está en su repo https://github.com/ourresearch/openalex-concept-tagging
###
####################################################

model = None
model_path = "teachers/openalex_extractor/model_files/"

# Load the dictionaries
with open(model_path + "topics_vocab.pkl", "rb") as f:
    target_vocab = pickle.load(f)

target_vocab_inv = {j: i for i, j in target_vocab.items()}

print("Loaded target vocab")

with open(model_path + "level_0_1_ids.pkl", "rb") as f:
    level_0_1_ids = pickle.load(f)

print("Loaded level 0 and level 1 IDs")

with open(model_path + "doc_type_vocab.pkl", "rb") as f:
    doc_vocab = pickle.load(f)

doc_vocab_inv = {j: i for i, j in doc_vocab.items()}

print("Loaded doc_type vocab")

with open(model_path + "journal_name_vocab.pkl", "rb") as f:
    journal_vocab = pickle.load(f)

journal_vocab_inv = {j: i for i, j in journal_vocab.items()}

print("Loaded journal vocab")

with open(model_path + "paper_title_vocab.pkl", "rb") as f:
    title_vocab = pickle.load(f)

title_vocab_inv = {j: i for i, j in title_vocab.items()}

print("Loaded title vocab")

with open(model_path + "tag_id_vocab.pkl", "rb") as f:
    tag_id_vocab = pickle.load(f)

print("Loaded tag ID vocab")

encoding_layer = tf.keras.layers.experimental.preprocessing.CategoryEncoding(  # type: ignore
    num_tokens=len(target_vocab) + 1, output_mode="binary", sparse=False
)

print("Encoding layer set up")

# Load the model components
raw_model = tf.keras.models.load_model(model_path + "model", compile=False)  # type: ignore
raw_model.trainable = False

print("Loaded raw model")

mag_model = tf.keras.Model(  # type: ignore
    inputs=raw_model.inputs, outputs=tf.math.top_k(raw_model.outputs, k=250)  # type: ignore
)
mag_model.trainable = False

for layer in mag_model.layers:
    if isinstance(layer, tf.keras.layers.Dropout) and hasattr(layer, "rate"):  # type: ignore
        layer.rate = 0.0

print("Created full model \n")


def invert_abstract_to_abstract(invert_abstract):
    invert_abstract = json.loads(invert_abstract)
    ab_len = invert_abstract["IndexLength"]

    if 30 < ab_len < 1000:
        abstract = [" "] * ab_len
        for key, value in invert_abstract["InvertedIndex"].items():
            for i in value:
                abstract[i] = key
        final_abstract = " ".join(abstract)
    else:
        final_abstract = None
    return final_abstract


def clean_abstract(abstract, inverted=True):
    if inverted:
        if abstract:
            abstract = invert_abstract_to_abstract(abstract)
        else:
            pass
    else:
        pass
    abstract = clean_text(abstract)
    return abstract


def clean_text(text):
    try:
        text = text.lower()

        text = re.sub("[^a-zA-Z0-9 ]+", " ", text)
        text = re.sub(" +", " ", text)
        text = text.strip()

    except:
        text = ""
    return text


def try_lowercase(text):
    try:
        text = text.lower()
    except:
        pass
    return text


def tokenize_feature(feature, feature_name="doc_type"):
    if feature_name == "doc_type":
        vocab = doc_vocab
    else:
        vocab = journal_vocab
    unk_token_id = vocab.get("[UNK]")
    none_token_id = vocab.get("[NONE]")
    if feature:
        token_feature = [vocab.get(feature, unk_token_id)]
    else:
        token_feature = [none_token_id]
    return token_feature


def tokenize_title(feature):
    split_feature = feature.split(" ")
    vocab = title_vocab
    unk_token_id = vocab.get("[UNK]")
    none_token_id = vocab.get("[NONE]")
    if feature:
        token_feature = [vocab.get(x, unk_token_id) for x in split_feature]
    else:
        token_feature = [none_token_id]
    return token_feature


def cut_length(data, seq_len=512):
    return data[:seq_len]


"""
Convierte el texto plano dado por el usuario en el input adecuado
para el modelo de extracción de conceptos.
"""


def convert_input_format(title, abstract=None):

    output = {
        "title": title,
        "abstract": abstract,
        "inverted_abstract": False,
        "journal": None,
        "doc_type": None,
    }

    return [output]


def transformation(dict_input):
    # Get input JSON data and convert it to a DF
    input_json = io.StringIO(json.dumps(dict_input))
    input_df = pd.read_json(input_json, orient="records").reset_index()

    # Tokenize data
    input_df["title"] = input_df["title"].apply(clean_text)
    input_df["abstract"] = input_df.apply(
        lambda x: clean_abstract(x.abstract, x.inverted_abstract), axis=1
    )
    input_df["journal"] = input_df["journal"].apply(try_lowercase)
    input_df["paper_title_tok"] = input_df["title"].apply(tokenize_title)
    input_df["abstract_tok"] = input_df["abstract"].apply(tokenize_title)
    input_df["doc_type_tok"] = input_df["doc_type"].apply(
        tokenize_feature, args=("doc_type",)
    )
    input_df["journal_tok"] = input_df["journal"].apply(
        tokenize_feature, args=("journal",)
    )

    input_df["paper_title_tok"] = input_df["paper_title_tok"].apply(
        cut_length, args=(32,)
    )
    input_df["abstract_tok"] = input_df["abstract_tok"].apply(cut_length, args=(256,))

    paper_titles = tf.ragged.constant(input_df["paper_title_tok"].to_list()).to_tensor(  # type: ignore
        shape=[None, 32]
    )
    abstracts = tf.ragged.constant(input_df["abstract_tok"].to_list()).to_tensor(  # type: ignore
        shape=[None, 256]
    )

    doc_types = tf.convert_to_tensor(input_df["doc_type_tok"].to_list())
    journal = tf.convert_to_tensor(input_df["journal_tok"].to_list())

    # Predict
    model_output = mag_model([paper_titles, abstracts, doc_types, journal])

    scores = model_output.values.numpy()[0].tolist()  # type: ignore
    preds = model_output.indices.numpy()[0].tolist()  # type: ignore

    # Transform predicted labels into tags (to get most likely concepts)
    all_tags = []
    # for score, pred, paper_id in zip(scores, preds, paper_ids):
    for score, pred in zip(scores, preds):
        pred_score_dict = {pred_i: score_j for pred_i, score_j in zip(pred, score)}
        tags = []
        tag_scores = []
        tag_ids = []
        # pred_ids = []

        for i in range(20):
            if (pred[i] in level_0_1_ids) & (score[i] >= 0.32):
                tags.append(target_vocab_inv.get(pred[i]))
                tag_scores.append(score[i])
                tag_ids.append(tag_id_vocab.get(pred[i]))
                # pred_ids.append(pred[i])
            elif score[i] >= 0.41:
                tags.append(target_vocab_inv.get(pred[i]))
                tag_scores.append(score[i])
                tag_ids.append(tag_id_vocab.get(pred[i]))
                # pred_ids.append(pred[i])
            else:
                pass
        if len(tags) == 0:
            tags.append(target_vocab_inv.get(pred[0]))
            tag_scores.append(score[0])
            tag_ids.append(tag_id_vocab.get(pred[0]))

        all_tags.append({"tags": tags, "scores": tag_scores, "tag_ids": tag_ids})

    # Transform predictions to JSON
    result = json.dumps(all_tags)
    return result
