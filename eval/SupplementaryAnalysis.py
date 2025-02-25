import json
import math
import string
from nltk.tokenize import sent_tokenize
import nltk
from nltk.corpus import stopwords
import re
nltk.download('stopwords')
import pandas

def remove_special_characters(s):
    pattern = r"[^a-zA-Z0-9\s]"
    return re.sub(pattern, " ", s)


def camel_case_split(s):
    result = []
    start = 0
    for i, c in enumerate(s[1:], 1):
        if c.isupper():
            result.append(s[start:i])
            start = i
    result.append(s[start:])
    return result

def calculateSIAInfo(comment:str,pMap:dict,code:str):
    commentTokens = nltk.word_tokenize(comment)
    code = remove_special_characters(code)
    codeTokens = nltk.word_tokenize(code)
    #print(codeTokens)
    newcodeToken = []
    for name in codeTokens:
        newcodeToken.append(name)
        newcodeToken.extend(camel_case_split(name))
    #print(newcodeToken)
    stopword = stopwords.words('english')
    stopword.extend(' '.join(string.punctuation).split(" "))
    stopword.extend("//")

    score = 0
    leftword = 0
    codeRelevantWordNum = 0
    codeRelevantWord = []
    for t in commentTokens:
        if(t=="//"):
            continue
        if(stopword.__contains__(t.lower())):
            continue
        if(newcodeToken.__contains__(t) or newcodeToken.__contains__(t.lower())):
            codeRelevantWordNum=codeRelevantWordNum+1
            codeRelevantWord.append(t)
            continue

        leftword=leftword+1
        if(not pMap.__contains__(t.lower())):
            continue
        #print(t)
        score = score-math.log(pMap[t.lower()])

    if(codeRelevantWordNum!=len(codeRelevantWord)):
        print(comment)
        print(codeRelevantWordNum)
        print(codeRelevantWord)
        print(code)
        print("--------------------------")
    return score, score/len(commentTokens),len(commentTokens),leftword,codeRelevantWordNum,codeRelevantWord


def analyze(src,dest,pMap_path):
    f = open(src, 'r', encoding='utf-8')
    fresult= open(dest, 'w', encoding='utf-8')

    fp = open(pMap_path, 'r', encoding='utf-8')
    pMap = dict()
    for line in fp.readlines():
        pMap = json.loads(line, strict=False)

    for line in f.readlines():
        data = json.loads(line, strict=False)
        id = data["aId"]
        code = data["code"]
        generationResult = data["generationResult"]
        for item in generationResult:
            comment = item["sentence"]
            SIA, mesia, commentlen, leftword,codeRelevantWordNum,codeRelevantWord = calculateSIAInfo(comment, pMap, code)

            item["SIA"] = SIA
            item["mesia"] = mesia
            item["commentLen"] = commentlen
            item["codeExtraWord"] = leftword
            item["codeRelevantWordNum"] = codeRelevantWordNum
            item["codeRelevantWord"] = codeRelevantWord
        jsonstr = json.dumps(data)
        fresult.writelines(jsonstr + "\n")

if __name__ == '__main__':

    # change strategy and paths.
    strategy = "IsComment"
    projects = ["ambari", "camel", "derby", "flink", "hadoop", "hbase", "jackrabbit", "lucene", "pdfbox", "wicket"]
    
    for p in projects:
        print(p)
        analyze(f"/data/zxl/IsComment-main/output/{strategy}/merge/{p}.json", 
                f"/data/zxl/IsComment-main/output/{strategy}/FinalResult/{p}.json",
                "/data/zxl/IsComment-main/eval/pMap.json")



