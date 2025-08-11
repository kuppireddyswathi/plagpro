from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

nltk.download('punkt')
nltk.download('stopwords')

def preprocess(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered = [word for word in words if word.isalnum() and word not in stop_words]
    return " ".join(filtered)

def check_duplicates_in_single_file(text):
    import re
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from nltk.tokenize import sent_tokenize

    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 30]
    
    # Save original structure
    original_structure = text

    cleaned_paragraphs = [' '.join(sent_tokenize(p)) for p in paragraphs]

    vectorizer = TfidfVectorizer().fit_transform(cleaned_paragraphs)
    similarity_matrix = cosine_similarity(vectorizer)

    total_score = 0
    total_comparisons = 0
    matched_lines = set()

    for i in range(len(paragraphs)):
        for j in range(i + 1, len(paragraphs)):
            sim = similarity_matrix[i][j] * 100
            total_score += sim
            total_comparisons += 1
            if sim > 30:
                matched_lines.add(paragraphs[i])
                matched_lines.add(paragraphs[j])

    avg_similarity = total_score / total_comparisons if total_comparisons else 0
    originality = round(100 - avg_similarity, 2)

    return {
        "report_text": f"Originality Score: {originality}%",
        "matched_lines": list(matched_lines),
        "originality_score": originality,
        "clean_text": original_structure  # ✅ return original structure
    }
