from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm
import json

model = SentenceTransformer('sentence-transformers/stsb-roberta-large')
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)

def cosine_similarity_score(x, y):
    from sklearn.metrics.pairwise import cosine_similarity
    cosine_similarity_matrix = cosine_similarity(x, y)
    return cosine_similarity_matrix

def getSemanticSimilarity(Src,Dest):
    src = Src.strip()
    dest = Dest.strip()
    data = [src, dest]
    data_emb = model.encode(data)
    sim = cosine_similarity_score(data_emb[0].reshape(1, -1), data_emb[1].reshape(1, -1))[0][0]
    return sim
