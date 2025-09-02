# paraphraser.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# ✅ Small model load (Render 512Mi కి safe)
MODEL_ID = "google/flan-t5-small"

# Tokenizer + model
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_ID,
    low_cpu_mem_usage=True  # saves memory
)

# Paraphrasing pipeline
paraphraser = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

def paraphrase_text(text: str, num_return_sequences: int = 1, max_length: int = 128):
    """
    Basic paraphrasing function using T5-small.
    Input: plain text
    Output: list of paraphrased variations
    """
    if not text.strip():
        return [""]

    # Construct simple prompt (T5 style)
    prompt = f"paraphrase: {text}"

    try:
        outputs = paraphraser(
            prompt,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.9,
        )

        return [o["generated_text"].strip() for o in outputs]

    except Exception as e:
        return [f"[Error during paraphrasing: {e}]"]


# # ✅ Local test
# if __name__ == "__main__":
#     sample = "Plagiarism detection helps maintain academic integrity."
#     results = paraphrase_text(sample, num_return_sequences=2)
#     print("\nInput:", sample)
#     for i, r in enumerate(results, 1):
#         print(f"Variation {i}: {r}")
