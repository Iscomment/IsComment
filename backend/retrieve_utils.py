import numpy as np
from Levenshtein import distance
import json

def get_code_to_issue(filename):
    try:
        f = open(filename, 'r', encoding='utf-8')
    except:
        return {}
    code_to_issue = {}
    code_name_to_issue = {}
    for line in f.readlines():
        try:
            data = json.loads(line, strict=False)
            code_to_issue[data["code"]] = data["issue"]
            # code_name_to_issue[data["name"]] = data["issueDescription"]
        except:
            continue
    return code_to_issue

def search_issue(query_code, issue_path):
    # https://rapidfuzz.github.io/Levenshtein/levenshtein.html#distance
    # scores = distance([query_code]*len(code_to_issue), "levenshtein")
    # tokenized_query = query_code.split(" ")
    # doc_scores = bm25.get_scores(tokenized_query)
    # sorted_indices = np.argsort(doc_scores)[::-1]
    # return [database[i] for i in sorted_indices][0]['issue']
    code_to_issue = get_code_to_issue(issue_path)
    if code_to_issue == {}:
        return "error"
    codes = list(code_to_issue.keys())
    scores = [distance(query_code, code) for code in codes]
    max_value = min(scores)
    if max_value > 10: return "none" 
    else: return code_to_issue[codes[scores.index(max_value)]]

    

