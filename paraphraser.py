from transformers import pipeline

# Use a small paraphrasing model
paraphraser = pipeline("text2text-generation", model="Vamsi/T5_Paraphrase_Paws")

def paraphrase_paragraphs(text):
    paragraphs = text.split('\n')
    output = []

    for para in paragraphs:
        if not para.strip():
            output.append("")
        elif len(para.strip()) < 20:
            output.append(para)
        else:
            result = paraphraser(para, max_length=256, num_return_sequences=1)[0]['generated_text']
            output.append(result)

    return "\n".join(output)
