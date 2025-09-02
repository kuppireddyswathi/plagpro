# # paraphraser.py
# import os
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# # ✅ Cache location safe గా మార్చు (Render free tier కోసం)
# os.environ["TRANSFORMERS_CACHE"] = "/tmp"

# # ✅ Smallest T5 model వాడు (base వాడితే OOM వచ్చే chance ఉంది)
# MODEL_ID = "google/flan-t5-small"

# # ✅ Load tokenizer & model
# tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
# model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)

# # ✅ Create pipeline once (fast for reuse)
# paraphraser = pipeline(
#     "text2text-generation",
#     model=model,
#     tokenizer=tokenizer,
#     device=-1   # CPU only (Render free tier కి safe)
# )

# def paraphrase_text(text: str, num_return_sequences: int = 1):
#     """
#     Simple paraphraser using flan-t5-small.
#     Returns list of paraphrased variations.
#     """
#     if not text.strip():
#         return ["[No input text]"]

#     prompt = f"Paraphrase the following text:\n{text}"

#     outputs = paraphraser(
#         prompt,
#         max_length=256,
#         num_return_sequences=num_return_sequences,
#         do_sample=True,
#         temperature=1.2,
#         top_p=0.95
#     )

#     return [o["generated_text"].strip() for o in outputs]
