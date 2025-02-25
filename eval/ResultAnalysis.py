import json
import seaborn as sns
import pandas
import matplotlib.pyplot as plt

MesiaLimit = 3.0
codeRelevantWordNumLimit = 1
IssueScoresLimit = 0.6

def RQ1Analysis(path:str,filter:bool):
    projects = ["ambari", "camel", "derby", "flink", "hadoop", "hbase", "jackrabbit", "lucene", "pdfbox", "wicket"]
    SentencesNum = 0
    AverageSentenceNum=0
    AverageSentenceLen=0
    SumLen=0
    FullCover=0
    PartialCover=0
    Nocover=0

    for p in projects:
        f = open(f"{path}/{p}.json", 'r', encoding='utf-8')
        Total = 0
        success = 0
        fullnum = 0
        partnum = 0
        fail = 0

        generatedNum = 0
        totalLen = 0

        print(p)
        for line in f.readlines():
            data = json.loads(line, strict=False)
            id = data["aId"]
            code = data["code"]
            GTList = data["SplitGT"]

            num = len(GTList)
            Total = Total + num

            generationResult = data["generationResult"]
            flag = []
            for i in range(num):
                flag.append(0)

            for item in generationResult:
                GTScores = list(item["GTScores"])
                maxScore = max(GTScores)

                # filtering by code relevancy and issue verifiablity.
                if filter==True:
                    if (item["codeRelevantWordNum"] < codeRelevantWordNumLimit and item["side"] < 0):
                        continue
                    if (float(max(item["IssueScores"])) < IssueScoresLimit):
                        continue

                # If SentenceBert > 0.6, regard as cover.
                if (float(maxScore) > 0.6):
                    flag[GTScores.index(maxScore)] = 1

                totalLen = totalLen + item["commentLen"]
                generatedNum = generatedNum + 1

            if (sum(flag) == num):
                fullnum = fullnum + 1
            elif sum(flag) > 0:
                partnum = partnum + 1
            else:
                fail = fail + 1

            success = success + sum(flag)

        SentencesNum = SentencesNum+generatedNum
        SumLen = SumLen+ totalLen

        FullCover = FullCover+fullnum
        PartialCover = PartialCover+partnum
        Nocover = Nocover+fail

    print("--------------------------------------------------------")
    print("AverageSentenceNum:"+str(SentencesNum/443))
    print("AverageSentenceLen:"+str(SumLen/SentencesNum))
    print("FullCover:"+str(FullCover))
    print("PartialCover:"+str(PartialCover))
    print("Nocover:"+str(Nocover))
    print("CoverRatio:"+str((FullCover+PartialCover)/443))

def RQ2Analysis(path:str):
    projects = ["ambari", "camel", "derby", "flink", "hadoop", "hbase", "jackrabbit", "lucene", "pdfbox", "wicket"]

    RV=0
    NRV=0
    RNV=0
    NRNV=0

    for p in projects:
        f = open(f"{path}/{p}.json", 'r', encoding='utf-8')
        Total = 0
        Relevant = 0
        Verified = 0

        comprehensiveResults = dict()
        comprehensiveResults[0] = dict()
        comprehensiveResults[0][0] = 0
        comprehensiveResults[0][1] = 0
        comprehensiveResults[1] = dict()
        comprehensiveResults[1][0] = 0
        comprehensiveResults[1][1] = 0

        print(p)

        for line in f.readlines():
            data = json.loads(line, strict=False)
            id = data["aId"]
            code = data["code"]
            generationResult = data["generationResult"]

            for item in generationResult:
                Total = Total + 1

                V = 0
                R = 0

                if (item["codeRelevantWordNum"] < codeRelevantWordNumLimit and item["side"] < 0):
                    R = 0
                else:
                    R = 1
                    Relevant = Relevant + 1

                if (float(max(item["IssueScores"])) < IssueScoresLimit):
                    V = 0
                else:
                    V = 1
                    Verified = Verified + 1

                comprehensiveResults[R][V] = comprehensiveResults[R][V] + 1

        print("---------------------------------")
        print(comprehensiveResults[0][0])
        print(comprehensiveResults[0][1])
        print(comprehensiveResults[1][0])
        print(comprehensiveResults[1][1])
        print("------------------------")

        RV=RV+comprehensiveResults[1][1]
        RNV=RNV+comprehensiveResults[1][0]
        NRV=NRV+comprehensiveResults[0][1]
        NRNV=NRNV+comprehensiveResults[0][0]

    sum = RV+RNV+NRV+NRNV

    print(f'Relevant & Verifiable           {RV} ({RV/sum})')
    print(f'Relevant & Not Verifiable       {RNV} ({RNV / sum})')
    print(f'Not Relevant & Verifiable       {NRV} ({NRV / sum})')
    print(f'Not Relevant & Not Verifiable   {NRNV} ({NRNV / sum})')

def getMESIA(project:str,array:[],path:str):
    f = open(f"{path}/{project}.json", 'r', encoding='utf-8')
    for line in f.readlines():
        data = json.loads(line, strict=False)
        generationResult = data["generationResult"]
        for item in generationResult:
            if (item["codeRelevantWordNum"] < codeRelevantWordNumLimit and item["side"] < 0):
                continue
            if (float(max(item["IssueScores"])) < IssueScoresLimit):
                continue
            array.append(item["mesia"])

def RQ3Analysis():
    projects = ["ambari", "camel", "derby", "flink", "hadoop", "hbase", "jackrabbit", "lucene", "pdfbox", "wicket"]
    codePrompt = []
    for p in projects:
        getMESIA(p, codePrompt, "D:\\finalResult\\codePrompt\\")

    codeIssuePrompt = []
    for p in projects:
        getMESIA(p, codeIssuePrompt, "D:\\finalResult\\codeIssuePrompt\\")

    TFIDF = []
    for p in projects:
        getMESIA(p, TFIDF, "D:\\finalResult\\TFIDF\\")

    DPR = []
    for p in projects:
        getMESIA(p, DPR, "D:\\finalResult\\DPR\\")

    DistillRoberta = []
    for p in projects:
        getMESIA(p, DistillRoberta, "D:\\finalResult\\DistillRoberta\\")

    codisnowPrompt = []
    for p in projects:
        getMESIA(p, codisnowPrompt, "D:\\finalResult\\codisnowPrompt\\")


    label=[]
    for i in range(codePrompt.__len__()):
        label.append("Sun et al.")
    for i in range(codeIssuePrompt.__len__()):
        label.append("No Retrieval")
    for i in range(TFIDF.__len__()):
        label.append("TFIDF")
    for i in range(DPR.__len__()):
        label.append("DPR")
    for i in range(DistillRoberta.__len__()):
        label.append("DistilRoBERTa")
    for i in range(codisnowPrompt.__len__()):
        label.append("Codisnow")

    all_data=[]
    all_data.extend(codePrompt)
    all_data.extend(codeIssuePrompt)
    all_data.extend(TFIDF)
    all_data.extend(DPR)
    all_data.extend(DistillRoberta)
    all_data.extend(codisnowPrompt)

    df = {'label': label,'all_data':all_data}
    sns.violinplot(x = label, y = all_data,density_norm='count',color="Green")
    plt.show()

if __name__ == '__main__':

    # change strategy and path.
    strategy = "IsComment"
    path = f"/data/zxl/IsComment-main/output/{strategy}/FinalResult"

    # If calculate the results after filtering, set True.
    RQ1Analysis(path,False)
    #RQ2Analysis(path)
    #RQ3Analysis()