from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Lazy load model
paraphraser = None

# Supported modes and styles
MODES = ["safe", "strong", "creative"]
STYLES = ["formal", "casual", "academic", "technical"]

# Model for Render / free tier
MODEL_NAME = "google/flan-t5-base"

def load_model():
    global paraphraser
    if paraphraser is None:
        print("Loading model... (~1GB, first run may take some time)")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        paraphraser = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

def paraphrase_paragraphs(text, mode="safe", style="formal", num_variations=2):
    """
    Paraphrase paragraphs with given mode and style using flan-t5-base.
    Supports 3 modes × 4 styles = 12 combinations.
    """
    global paraphraser
    load_model()
    
    if mode not in MODES:
        raise ValueError(f"Invalid mode. Choose from {MODES}")
    if style not in STYLES:
        raise ValueError(f"Invalid style. Choose from {STYLES}")
    
    paragraphs = text.split("\n")
    output = []

    for para in paragraphs:
        if not para.strip():
            output.append([])
            continue
        if len(para.strip().split()) < 5:
            output.append([para])
            continue

        prompt = (
            f"Rewrite the following paragraph naturally, keeping the meaning the same, "
            f"in a {style} style and with {mode} paraphrasing:\n{para}"
        )

        result = paraphraser(
            prompt,
            max_new_tokens=256,
            num_return_sequences=num_variations,
            do_sample=True,
            top_k=200,
            top_p=0.95,
            temperature=1.3
        )

        variations = [r['generated_text'].strip() for r in result]
        output.append(variations)

    return output
