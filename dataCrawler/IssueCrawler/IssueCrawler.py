import os.path

import requests
import json
import time

api_url = 'https://issues.apache.org/jira/rest/api/2/search'

def crawler(project):
    # Set up the query to retrieve all issues in the project
    if not os.path.exists(f"D:\Python\IssueCrawler\{project}"):
        os.mkdir(f"D:\Python\IssueCrawler\{project}")

    query = {'jql': f"project={project}"}
    # Set up the pagination parameters
    start_at = 0
    max_results = 50
    # Retrieve all issues in the project
    while True:
        # Set up the pagination parameters for the current request
        query['startAt'] = start_at
        query['maxResults'] = max_results
        try:
            # Send the API request and retrieve the response
             response = requests.get(api_url, params=query)
            # Parse the JSON response and extract the issue data
             data = json.loads(response.text)
             issues = data['issues']
        except:
             time.sleep(10)
             continue

        # Process the issue data
        for issue in issues:
            # Retrieve the comments for the current issue
            issue_url = f"https://issues.apache.org/jira/rest/api/2/issue/{issue['key']}"

            try:
                issue_response = requests.get(issue_url)
                issue_data = json.loads(issue_response.text)
            except:
                time.sleep(10)
                continue

            jsondata = json.dumps(issue_data, indent=4)
            with open(f"D:\Python\IssueCrawler\{project}\{issue['key']}.json", 'w', encoding='utf-8') as f:
                f.write(jsondata)

            print(f"{issue['key']} successfully downloaded!")

        # Check if there are more issues to retrieve
        if start_at + max_results >= data['total']:
            break

        # Update the pagination parameters for the next request
        start_at += max_results

if __name__=="__main__":
    crawler("AMBARI")
    crawler("CAMEL")
    crawler("DERBY")
    crawler("FLINK")
    crawler("HADOOP")
    crawler("HBASE")
    crawler("JCR")
    crawler("LUCENE")
    crawler("PDFBOX")
    crawler("WICKET")