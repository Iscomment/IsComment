from sentence_transformers import SentenceTransformer, models, InputExample, losses, util
from transformers import AutoTokenizer, AutoModel
import torch
import sys,os
import torch.nn.functional as F
from sentence_transformers import evaluation
from tqdm import tqdm
import json
from nltk.tokenize import sent_tokenize
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    # First element of model_output contains all token embeddings
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(
        -1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

checkPointFolder = "./SIDE/baseline-20240110T050554Z-001/baseline/103080" #specify the path to the best-performing checkpoint

tokenizer = AutoTokenizer.from_pretrained(checkPointFolder)
model = AutoModel.from_pretrained(checkPointFolder).to(device)

def SIDE(method, comment):
    pair = [method,comment]
    encoded_input = tokenizer(pair, padding=True, truncation=True, return_tensors='pt').to(device)
    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)
    # Perform pooling
    sentence_embeddings = mean_pooling(
        model_output, encoded_input['attention_mask'])
    # Normalize embeddings
    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
    sim = util.pytorch_cos_sim(
        sentence_embeddings[0], sentence_embeddings[1]).item()
    return sim