# # citation_checker.py
# import re

# def check_citations(text):
#     lines = text.split('\n')

#     # 1. Extract both APA and IEEE-style in-text citations
#     apa_citations = re.findall(r'\(([^()]+?, \d{4})\)', text)
#     ieee_citations = re.findall(r'\[(\d+)\]', text)

#     # 2. Detect references section
#     references_start = -1
#     for i, line in enumerate(lines):
#         if line.strip().lower() in ['references', 'bibliography', 'works cited']:
#             references_start = i
#             break

#     references = lines[references_start + 1:] if references_start != -1 else []

#     # 3. APA-style check: author name must be in references
#     missing_apa = []
#     for citation in apa_citations:
#         author = citation.split(',')[0].strip()
#         found = any(author.lower() in ref.lower() for ref in references)
#         if not found:
#             missing_apa.append(citation)

#     # 4. IEEE-style check: citation number must appear in references
#     missing_ieee = []
#     if ieee_citations:
#         max_cite = max(map(int, ieee_citations))
#         ref_count = len(references)
#         if max_cite > ref_count:
#             missing_ieee = [f"[{i}]" for i in range(1, max_cite + 1) if i > ref_count]

#     # 5. Build final result message
#     result = ""

#     if not apa_citations and not ieee_citations:
#         result += "⚠️ No in-text citations found.\n"

#     if references_start == -1:
#         result += "⚠️ No references section found.\n"

#     if missing_apa:
#         result += "⚠️ Missing APA-style citations in references:\n" + "\n".join(missing_apa) + "\n"

#     if missing_ieee:
#         result += "⚠️ Missing IEEE-style citations in references:\n" + "\n".join(missing_ieee)

#     if not result:
#         result = "✅ All in-text citations are present in references."

#     return result
