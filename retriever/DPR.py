import os
import json
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("facebook-dpr-ctx_encoder-single-nq-base")

def search(code:str,issue:list[str]):
    issue_embs = model.encode(issue, convert_to_tensor=True)
    query_emb = model.encode(code, convert_to_tensor=True)
    hits = util.semantic_search(query_emb, issue_embs,top_k=5)[0]
    resultSentences=[]
    resultScores=[]
    for top_hit in hits:
        resultSentences.append(issue[top_hit['corpus_id']])
        resultScores.append(top_hit['score'])
        #print(issue_embs[top_hit['corpus_id']])
        #print("Cossim: {:.2f}".format(top_hit['score']))
        #print("\n\n")
    print(code)
    print(resultSentences)
    print(resultScores)
    print("\n\n")
    return resultSentences,resultScores

def process(src,dest):
    f = open(src, 'r', encoding='utf-8')
    fResult = open(dest, 'w', encoding='utf-8')
    #fResult1 = open(dest+"View", 'w', encoding='utf-8')
    num = 0
    for line in f.readlines():
        num = num + 1
        print(num)
        data = json.loads(line, strict=False)
        id = data["aId"]
        code = data["code"]
        comment = data["comment"]
        issueId = data["issueId"]
        issueStringList = data["issueStringList"]
        issueSearchSentences, issueSearchScores = search(code, issueStringList)

        data["issueSearchSentences"] = issueSearchSentences
        data["issueSearchScores"] = issueSearchScores
        str = json.dumps(data)
        fResult.writelines(str + "\n")


if __name__ == "__main__":
    process("C:\\Users\\user\\Desktop\\data\\ambari.json", "C:\\Users\\user\\Desktop\\DPR\\ambari.json")
    process("C:\\Users\\user\\Desktop\\data\\camel.json", "C:\\Users\\user\\Desktop\\DPR\\camel.json")
    process("C:\\Users\\user\\Desktop\\data\\derby.json", "C:\\Users\\user\\Desktop\\DPR\\derby.json")
    process("C:\\Users\\user\\Desktop\\data\\flink.json", "C:\\Users\\user\\Desktop\\DPR\\flink.json")
    process("C:\\Users\\user\\Desktop\\data\\hadoop.json", "C:\\Users\\user\\Desktop\\DPR\\hadoop.json")
    process("C:\\Users\\user\\Desktop\\data\\hbase.json", "C:\\Users\\user\\Desktop\\DPR\\hbase.json")
    process("C:\\Users\\user\\Desktop\\data\\jackrabbit.json", "C:\\Users\\user\\Desktop\\DPR\\jackrabbit.json")
    process("C:\\Users\\user\\Desktop\\data\\lucene.json", "C:\\Users\\user\\Desktop\\DPR\\lucene.json")
    process("C:\\Users\\user\\Desktop\\data\\pdfbox.json", "C:\\Users\\user\\Desktop\\DPR\\pdfbox.json")
    process("C:\\Users\\user\\Desktop\\\data\\wicket.json", "C:\\Users\\user\\Desktop\\DPR\\wicket.json")
