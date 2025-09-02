from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Local folder lo model unte path ivvu (download chesina flan-t5-small for example)
MODEL_PATH = "./flan-t5-small"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)

def paraphrase_text(text: str):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(
        **inputs,
        max_length=256,
        num_return_sequences=1,
        do_sample=True,
        temperature=1.2,
        top_p=0.9
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Test
if __name__ == "__main__":
    print(paraphrase_text("Plagiarism detection is an important task in academia."))
