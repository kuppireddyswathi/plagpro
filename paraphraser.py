from transformers import pipeline

# Model will load only when first request comes
paraphraser = None

def paraphrase_paragraphs(text):
    global paraphraser

    # Lazy load the model only when needed
    if paraphraser is None:
        paraphraser = pipeline(
            "text2text-generation",
            model="Vamsi/T5_Paraphrase_Paws"
        )

    paragraphs = text.split('\n')
    output = []

    for para in paragraphs:
        if not para.strip():
            output.append("")
        elif len(para.strip()) < 20:
            output.append(para)
        else:
            result = paraphraser(
                para,
                max_length=256,
                num_return_sequences=1
            )[0]['generated_text']
            output.append(result)

    return "\n".join(output)
