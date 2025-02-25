from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm
import json


# we downloaded the model. You can also use huggingface to get the model.
model = SentenceTransformer('/home/user/pxl/sentenceBert/stsb-roberta-large')
device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
model.to(device)
print("model loaded!")



def cosine_similarity_score(x, y):
    from sklearn.metrics.pairwise import cosine_similarity
    cosine_similarity_matrix = cosine_similarity(x, y)
    return cosine_similarity_matrix


def getSemanticSimilarity(A,B):
    a = A.strip()
    b = B.strip()
    data = [a, b]
    data_emb = model.encode(data)
    css = cosine_similarity_score(data_emb[0].reshape(1, -1), data_emb[1].reshape(1, -1))[0][0]
    return css

def processCodePrompt(project:str, strategy:str):
    print(project)


    # change paths.
    f = open(f"/data/zxl/IsComment-main/output/{strategy}/SplitResult/{project}.json", 'r', encoding='utf-8')
    fresults = open(f"/data/zxl/IsComment-main/output/{strategy}/BertResult/{project}.json", 'w', encoding='utf-8')
    for line in tqdm(f.readlines()):
        data = json.loads(line, strict=False)
        GTList = data["SplitGT"]
        issueStringList = data["issueStringList"]
        commentList = data["splitSentences"]

        generationResult=[]

        for comment in commentList:
            item=dict()
            item["sentence"] = comment
            gtscores = []
            for gt in GTList:
                score = getSemanticSimilarity(comment,gt)
                gtscores.append(str(score))

            item["GTScores"] = gtscores

            issueScores = []
            for issueS in issueStringList:
                score = getSemanticSimilarity(comment,issueS)
                issueScores.append(str(score))

            item["IssueScores"] = issueScores

            generationResult.append(item)

        data["generationResult"]=generationResult
       
        jsonstr = json.dumps(data)
        fresults.writelines(jsonstr + "\n")

if __name__ == "__main__":

    # change strategy.
    strategy = "IsComment"
    projects = ["ambari", "camel", "derby", "flink", "hadoop", "hbase", "jackrabbit", "lucene", "pdfbox", "wicket"]

    for p in projects:
        print(p)
        processCodePrompt(p, strategy)
    
