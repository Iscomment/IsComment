import json
import math
import string
from nltk.tokenize import sent_tokenize
import nltk
from nltk.corpus import stopwords
import re
nltk.download('stopwords')

def remove_special_characters(string):
    pattern = r"[^a-zA-Z0-9\s]"
    return re.sub(pattern, " ", string)

def camel_case_split(s):
    result = []
    start = 0
    for i, c in enumerate(s[1:], 1):
        if c.isupper():
            result.append(s[start:i])
            start = i
    result.append(s[start:])
    return result

def calculateSIA(comment:str,pMap:dict,code:str):
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



if __name__ == '__main__':

    code="public void setIncludeHeaders(String includeHeaders) {\n        this.includeHeaders = includeHeaders;\n    }"
    comment="A regex that defines which Camel headers are also included as MIME headers into the MIME multipart."

    fp = open("D:\\Codisnow\\eval\\pMap.json", 'r', encoding='utf-8')
    pMap = dict()
    for line in fp.readlines():
        pMap = json.loads(line, strict=False)

    SIA, Mesia, commentlen, leftword, codeRelevantWordNum, codeRelevantWord = calculateSIA(comment, pMap, code)

    print(Mesia)
    print(codeRelevantWordNum)
    print(codeRelevantWord)

