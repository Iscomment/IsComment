from nltk.tokenize import sent_tokenize
import json
from tqdm import tqdm
import re


def remainComments(input_text):
    pattern = r"(?:Code Comments:?)([\s\S]*?)(?=\n\s*\n|$)"
    matches = re.findall(pattern, input_text)
   
    return "\n".join(matches)

# remove noises in LLM-generated results, sometimes LLM not only output the comment we need, but also code......
# If you use other LLMs, maybe need to add some heuristic rules to remove various kinds of noises.
def processCodeComment(codeComments:str):
    results = []
    lines = codeComments.split("\n")
    for i in range(len(lines)):
        cur = lines[i].strip()
        if (cur.startswith("/**")):
            continue
        if (cur.startswith("*/")):
            continue
        if (cur.startswith("public") or cur.startswith("private") or cur.startswith("protected") or cur.startswith("@Deprecated")):
            break
        cur = cur.lstrip("*").strip()
        cur = cur.lstrip("/").strip()
        cur = cur.lstrip("-").strip()
        if(cur==""):
            continue
        sentence = sent_tokenize(cur)
        results.extend(sentence)

    L = []
    lenth = len(results)
    j = 0
    while j < lenth:
        cur = results.__getitem__(j)
        if (str(cur).startswith("Here") and str(cur).endswith(":")):
            L.append(cur)
            j = j + 1
            continue
        while ((not str(cur).strip().endswith(".")) and j + 1 < lenth and (not (
                str(results.__getitem__(j + 1)).strip().__getitem__(0).isupper() and not str(
            results.__getitem__(j + 1)).strip().__getitem__(1).isupper() or str(
            results.__getitem__(j + 1)).strip().__getitem__(0).__eq__("@")))):
            j = j + 1
            cur = cur + " " + str(results.__getitem__(j)).strip()
        L.append(cur)
        j = j + 1

    newSplitSentence = []
    for s in L:
        s = s.lstrip(":").strip()
        s = s.lstrip("/").strip()
        s = s.lstrip("*").strip()
        s = s.lstrip("/").strip()
        if (s == "" or s == "<p>"):
            continue
        newSplitSentence.append(s)
    return newSplitSentence


def split(src,dest):
    f = open(src, 'r', encoding='utf-8')
    fresults = open(dest, 'w', encoding='utf-8')
    lines = f.readlines()
    for line in tqdm(lines):
        data = json.loads(line, strict=False)
        results = data["result"]
        
        if need_extract:
            results = remainComments(results)

        splitSentences = processCodeComment(results)
        data["splitSentences"] = splitSentences
        jsonstr = json.dumps(data)
        fresults.writelines(jsonstr + "\n")


if __name__ == '__main__':

    # When use IsComment, LLM will output up to 5 kinds of comments and relevant issue sentences.
    # For evaluation, we need to extract only comments!
    # If you use other prompts, such as codePrompt, set it to False.
    need_extract = True

    # change strategy and paths.

    strategy = "IsComment"
    projects = ["ambari", "camel", "derby", "flink", "hadoop", "hbase", "jackrabbit", "lucene", "pdfbox", "wicket"]
    for p in projects:
        print(p)
        split(f"/data/zxl/IsComment-main/output/{strategy}/result/{p}.json",
              f"/data/zxl/IsComment-main/output/{strategy}/SplitResult/{p}.json")
