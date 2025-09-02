from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

MODEL_ID = "google/flan-t5-small"   # ✅ much lighter

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)

paraphraser = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
def paraphrase_paragraphs(text, num_variations=3, max_length=256):
    """
    Simple paraphraser using T5 model.
    No modes, no styles. Just generates paraphrased versions.
    Returns: list[list[str]] (variations for each paragraph)
    """
    paragraphs = text.split("\n")
    output = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            output.append([])
            continue
        if len(para.split()) < 5:
            output.append([para])  # too short
            continue

        # Create prompt for T5
        prompt = f"paraphrase: {para}"

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

        # Collect variations
        variations = []
        for _ in range(num_variations):
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                num_beams=5,
                num_return_sequences=1,
                temperature=1.2,
                top_p=0.9,
                do_sample=True
            )
            text_out = tokenizer.decode(outputs[0], skip_special_tokens=True)
            variations.append(text_out)

        output.append(variations)

    return output


# Local test
if __name__ == "__main__":
    text = """Plagiarism detection is an important task in academia.
It ensures originality and academic integrity.
Our system aims to detect copied content effectively."""

    results = paraphrase_paragraphs(text, num_variations=2)
    for i, para in enumerate(results):
        print(f"\nParagraph {i+1}:")
        for j, v in enumerate(para):
            print(f"Option {j+1}: {v}")
