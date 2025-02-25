import json
import openai
import os
from tqdm import tqdm

def codePrompt(code,issue):
    return f'Please generate a short comment in one sentence for the following function:\n{code}\n'

def codeIssuePrompt(code,issue):
    return f'The issue report is proposed before the code is commited to codebase and can provide supplementary information about the code. Please read the following issue, then generate code comments for the code. \n\n' \
           f'Issue:\n{issue}\n\n' \
           f'Code:\n{code}\n'

def codeIssueRetrievelPrompt(code,issueSentences):
    return f'The issue report is proposed before the code is commited to codebase and can provide supplementary information about the code to its code comments. Please read the following issue sentences searched from issue using the code, then generate code comments for the code. ' \
           f'Issue Sentences: \n{issueSentences}\n\n' \
           f'Code:\n {code}\n'

def IscommentExtractionPrompt(code,issue):
    return f'I will give you a code snippet and an issue report. The issue report is proposed before the code is commited to the codebase. ' \
           f'Please read the issue report sentence by sentence, then please identify the sentences in the issue report that are helpful to generate ' \
           f'code comments for the code and remember to excludes other irrelevant sentences or code snippets. ' \
           f'Remember that you need to obey the following output format: output each relevant sentence of the issue report in one line, ' \
           f'and at the end of each line output the releated aspect in "{{}}", such as (Functionality).\n' \
           f'To identify whether a sentence is helpful for generating code comments for the code, you can pay attention that whether the sentence provide the following aspects of information about the code:' \
           f'(1) Functionality: describe what the code does in turns of functionality. For example, the sentence "Tried to convert the given value to the requested type." describes the Functionality of the method named "tryConvertTo".\n' \
           f'(2) Concept: describe the meaning of terms used to name the code. For example, the sentence "Zombie leader is a replica won the election but does not exist in clusterstate." describes the Concept of the method named "getZombieLeader".\n' \
           f'(3) Directive: describe what are allowed or not allowed to do with the code. For example, the sentence "Must be followed by a call to #clearSnapshot(SortedMap)." describes the Directive of the method named "snapshot".\n' \
           f'(4) Rationale: describe the purpose or design rationale of the code. For example, the sentence "When sending messages to the control channel without using a DynamicRouterControlMessage, specify the Predicate by using this URI param." describes the Rationale of the method named "setPredicateBean".\n' \
           f'(5) Implication：describe the potential implication of the code, such as performance issues, etc. For example, the sentence "Pauses the Pulsar consumers. Once paused, a Pulsar consumer does not request any more messages from the broker." describes the Implication of the method named "doSuspend".\n' \
           f'Issue:\n{issue}\n\n' \
           f'Code:\n{code}\n'

def IscommentCommentGenerationPrompt(code,funSentences,conceptSentences,directSentences,rationaleSentences,impliSentences):
    return f'Please generate code comments to explain the code according to the following supplementary information retrieved from Issue.' \
           f'For each aspect, you need to output “Code Comments” in one line, then output the corresponding aspect of code comments for the ' \
           f'code snippet based on the retrieved issue sentences in the following lines.' \
           f'' \
           f'Supplementary Information:\n' \
           f'(1) Functionality: {funSentences}\n' \
           f'(2) Concept: {conceptSentences}\n' \
           f'(3) Directive: {directSentences}\n' \
           f'(4) Rationale: {rationaleSentences}\n' \
           f'(5) Implication: {impliSentences}\n' \
           f'' \
           f'Code:\n {code}'

def remove_quotes(s):
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s

def prompt(promptString):
    result = ""
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo', messages=[
                {"role": "system", "content": "You are an expert programmer."},
                {"role": "user", "content": promptString}
            ],
            temperature=0
        )
        result = response.choices[0]['message']['content']
    except:
        result = ""
    return result

def Generate(src,dest):
    f = open(src, 'r', encoding='utf-8')
    fResult = open(dest, 'w', encoding='utf-8')
    num = 0
    lines = f.readlines()
    print("start generating:")
    for line in tqdm(lines):
        num = num + 1
        print(num)
        try:
            data = json.loads(line, strict=False)
            id = data["aId"]
            code = data["code"]
            comment = data["comment"]
            issueId = data["issueId"]
            issueString = data["issueString"]
            issueStringList = data["issueStringList"]
            SplitGT = data["SplitGT"]

            codePromptResult = prompt(codePrompt(code,issueString))
            codePromptResult = remove_quotes(codePromptResult)
            print(codePromptResult)

            result = dict()
            result["aId"] = id
            result["code"] = code
            result["comment"] = comment
            result["issueId"] = issueId
            result["result"] = codePromptResult
            result["issueStringList"] = issueStringList
            result["SplitGT"] = SplitGT
        except:
            continue

        resultStr = json.dumps(result)
        fResult.writelines(resultStr + "\n")

if __name__ == "__main__":
    
    # change strategy, and the paths where you store data and results.

    strategy = "codePrompt"
    projects = ["ambari", "camel", "derby", "flink", "hadoop", "hbase", "jackrabbit", "lucene", "pdfbox", "wicket"]
    for p in projects:
        print(p)
        Generate(f"/data/zxl/IsComment-main/data/{p}.json",
                 f"/data/zxl/IsComment-main/output/{strategy}/result/{p}.json")