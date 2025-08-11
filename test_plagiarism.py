import nltk
nltk.data.path.append("C:/Users/K Swathi/AppData/Roaming/nltk_data")

from plagiarism_checker import check_plagiarism

# Sample known texts (you can add more later)
known_texts = [
    "Artificial intelligence is a branch of computer science that focuses on creating intelligent machines.",
    "Machine learning allows computers to learn from data and make predictions or decisions.",
    "Plagiarism is the act of using someone else's words or ideas without proper attribution."
]

# User input to test
test_input = """
Artificial intelligence is a branch of computer science that focuses on creating intelligent machines.
This technology is evolving rapidly and has many applications.
"""

# Run the plagiarism check
report = check_plagiarism(test_input, known_texts)

# Display result
print("=== PLAGIARISM REPORT ===")
for doc, score in report:
    print(f"{doc}: {score}% similarity")
