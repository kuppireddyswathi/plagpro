import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_API_TOKEN")  # must match the key in Render
if not HF_TOKEN:
    raise ValueError("HF_API_TOKEN environment variable not set!")

MODEL_ID = "google/flan-t5-base"
client = InferenceClient(token=HF_TOKEN)
# Supported modes and styles
MODES = ["safe", "strong", "creative"]
STYLES = ["formal", "casual", "academic", "technical"]

def paraphrase_paragraphs(text, mode="safe", style="formal", num_variations=2):
    """
    Paraphrase paragraphs using Hugging Face hosted T5 model.
    Supports 3 modes × 4 styles = 12 combinations.
    Returns list of paragraphs, each containing multiple variations.
    """
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

        variations = []
        for _ in range(num_variations):
            try:
                resp = client.text_generation(
                    model=MODEL_ID,
                    inputs=prompt,
                    max_new_tokens=256,
                    do_sample=True,
                    temperature=1.3,
                    top_k=200,
                    top_p=0.95
                )
                variations.append(resp.generated_text.strip())
            except Exception as e:
                variations.append(f"[Error generating paraphrase: {e}]")

        output.append(variations)

    return output

# # Optional local test
# if __name__ == "__main__":
#     test_text = """Plagiarism detection is an important task in academia.
# It ensures originality and academic integrity.
# Our system aims to detect copied content effectively."""

#     results = paraphrase_paragraphs(test_text, mode="creative", style="academic", num_variations=3)
#     for i, para in enumerate(results):
#         print(f"\nParagraph {i+1} variations:")
#         for j, v in enumerate(para):
#             print(f"Option {j+1}: {v}")
