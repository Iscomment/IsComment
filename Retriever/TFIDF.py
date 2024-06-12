import json
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

dir_path = "C:\\Users\\user\\Desktop\\data"
write_path = "C:\\Users\\user\\Desktop\\tfidf_data"


def process_tfidf_similarity(code, issue_sents):
    vectorizer = TfidfVectorizer()
    issue_sents.insert(0, code)
    embeddings = vectorizer.fit_transform(issue_sents)
    cosine_similarities = cosine_similarity(embeddings[0:1], embeddings[1:]).flatten()
    indexes = sorted(range(len(cosine_similarities)), key=lambda k: cosine_similarities[k], reverse=True)
    return indexes


if __name__ == "__main__":
    files = os.listdir(dir_path)
    for file_name in files:
        # if not file_name.endswith("camel.json"): continue
        file_path = os.path.join(dir_path, file_name)
        print(file_path)
        file = open(file_path, 'r')
        write_string = ""
        for i, line in enumerate(file):
            json_data = json.loads(line, strict=False)
            a_id = json_data['aId']
            comment = json_data['comment']
            code = json_data['code']
            issue_sents = json_data['issueStringList']
            issue_sents = [sent for sent in issue_sents if len(sent) != 0]
            indexes = process_tfidf_similarity(code, issue_sents)
            code_sim_issue_tf_idf_index = [int(i) for i in indexes]
            code_sim_issue_tf_idf_string = [issue_sents[i] for i in code_sim_issue_tf_idf_index]
            json_data['code_sim_issue_tf_idf_index'] = code_sim_issue_tf_idf_index
            json_data['code_sim_issue_tf_idf_string'] = code_sim_issue_tf_idf_string


            write_string += json.dumps(json_data) + "\n"
            # break

        write_file = open(os.path.join(write_path, file_name), "w")
        write_file.write(write_string)