import json
import os

path = "D:\Python\IssueCrawler"

def process( project):
    dir = path+"\\"+project
    files = os.listdir(dir)

    for file in files:
        fpath = dir+"\\"+file
        print(fpath)

        with open(fpath, "r") as f:
            data = json.load(f)

        # print(data['fields']['summary'])
        # print(data['fields']['description'])

        mydata = dict()
        mydata['summary'] = data['fields']['summary']
        mydata['description'] = data['fields']['description']
        mydata['body'] = []
        comments = data['fields']['comment']['comments']
        for comment in comments:
            # print(comment['body'])
            mydata['body'].append(comment['body'])
        jsondata = json.dumps(mydata, indent=4)
        if not os.path.exists(f"D:\IssueData\{project}"):
            os.mkdir(f"D:\IssueData\{project}")
        with open(f"D:\IssueData\{project}\{file}", "w", encoding='utf-8') as nf:
            nf.write(jsondata)

if __name__=="__main__":
    process("AMBARI")
    process("CAMEL")
    process("DERBY")
    process("FLINK")
    process("HADOOP")
    process("HBASE")
    process("JCR")
    process("LUCENE")
    process("PDFBOX")
    process("WICKET")
