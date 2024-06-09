# Python backend, POST request
# input: json
# {
#   "code": inp_code,
#   "config": a dict to save all comment types
# }
# output: json
# {
# "input": save the model input for debug,
# "output": generated comment,
# }
#

import json
import flask
from flask import request, jsonify

from openai_proxy import completions_with_backoff

from retrieve_utils import search_issue

app = flask.Flask(__name__)

def codePrompt(code):
    return f'Please generate a comment in three sentences for the following function:\n{code}\n'

def icom_prompt(code,issue,config):
    prompt = f'I will give you a code snippet and an issue report. ' \
        f'Please read the issue report sentence by sentence carefully, ' \
        f'then please identify the sentences in the issue report that can help generate code comments for the code snippets. ' \
        f'Remember that you need to focus on the most relevant sentences that can provide the following aspects of supplementary information about the code snippet:\n' \
    
    types = ['Functionality', 'Concept', 'Directive', 'Rationale', 'Implication']
    info_type = {
        'Functionality': 'Functionality: describe what the code does in turns of functionality. \n \
            For example, the sentence "Tried to convert the given value to the requested type." describes the Functionality of the method named "tryConvertTo".\n',
        'Concept': 'Concept: explain the meaning of terms used to name the code.\n \
            For example, the sentence "Zombie leader is a replica won the election but does not exist in clusterstate." describes the Concept of the method named "getZombieLeader".\n',
        'Directive': 'Directive: describe what are allowed or not allowed to do with the code.\n \
            For example, the sentence "Must be followed by a call to #clearSnapshot(SortedMap)." describes the Directive of the method named "snapshot".\n',
        'Rationale': 'Rationale: describe the purpose or design rationale of the code.\n \
            For example, the sentence "When sending messages to the control channel without using a DynamicRouterControlMessage, specify the Predicate by using this URI param." describes the Rationale of the method named "setPredicateBean".\n',
        'Implication': 'Implication: describe the potential implication of the code, such as performance issues, etc.\n \
            For example, the sentence "Pauses the Pulsar consumers. Once paused, a Pulsar consumer does not request any more messages from the broker." describes the Implication of the method named "doSuspend".\n'
    }
    output_type = {
        'Functionality': 'Functionality: functionality_comment_content\n',
        'Concept': 'Concept: concept_comment_content\n',
        'Directive': 'Directive: directive_comment_content\n',
        'Rationale': 'Rationale: rationale_comment_content\n',
        'Implication': 'Implication: implication_comment_content\n'
    }

    for key in types:
        if config[key] == True:
            prompt += info_type[key]
    
    prompt += f'Remember that please select the most relevant sentences and exclude any irrelevant sentences in the issue report.\n' \
        f'Please output information for each aspect in the following format:\n' \
        f'First, for each aspect, you need to output its name. ' \
        f'Second, for each aspect, you need to output the corresponding aspect of code comments for the code snippet based on the code and identified relevant sentences in issue. ' \
        f'If there are no relevant sentence identified in the issue report, you also need to output the name of the aspect and generate a code comment based on the code, please do not output "No relevant sentence identified in the issue report."\n' \
        f'DO NOT OUTPUT "No relevant sentence identified in the issue report."!!!\n' \
        f'Code Snippet:\n{code}\n\n'\
        f'Issue Report:\n{issue}\n\n' \
        f'DO NOT OUTPUT "No relevant sentence identified in the issue report."!!!\n' \
        f'Ouput format:\n'\
        
    for key in types:
        if config[key] == True:
            prompt += output_type[key]
    return prompt

#
def knowledgeGuidedPrompt(code,issue):
    return f'I will give you a code snippet and an issue report. ' \
           f'Please read the issue report sentence by sentence carefully, ' \
           f'then please identify the sentences in the issue report that can help generate code comments for the code snippets. ' \
           f'Remember that you need to focus on the most relevant sentences that can provide the following aspects of supplementary information about the code snippet:\n' \
           f'(1) Functionality: describe what the code does in turns of functionality. \n' \
           f'For example, the sentence "Tried to convert the given value to the requested type." describes the Functionality of the method named "tryConvertTo".\n' \
           f'(2) Concept: explain the meaning of terms used to name the code.\n' \
           f'For example, the sentence "Zombie leader is a replica won the election but does not exist in clusterstate." describes the Concept of the method named "getZombieLeader".\n' \
           f'(3) Directive: describe what are allowed or not allowed to do with the code.\n' \
           f'For example, the sentence "Must be followed by a call to #clearSnapshot(SortedMap)." describes the Directive of the method named "snapshot".\n' \
           f'(4) Rationale: describe the purpose or design rationale of the code.\n' \
           f'For example, the sentence "When sending messages to the control channel without using a DynamicRouterControlMessage, specify the Predicate by using this URI param." describes the Rationale of the method named "setPredicateBean".\n' \
           f'(5) Implication: describe the potential implication of the code, such as performance issues, etc.\n' \
           f'For example, the sentence "Pauses the Pulsar consumers. Once paused, a Pulsar consumer does not request any more messages from the broker." describes the Implication of the method named "doSuspend".\n' \
           f'' \
           f'' \
           f'Remember that please select the most relevant sentences and exclude any irrelevant sentences in the issue report.\n' \
           f'Please output information for each aspect in the following format:\n' \
           f'First, for each aspect, you need to output its name in one line, such as "Functionality:"\n' \
           f'Second, for each aspect, you need to output the corresponding aspect of code comments for the code snippet based on the code and identified relevant sentences in issue. ' \
           f'If there are no relevant sentence identified in the issue report, you also need to output the name of the aspect and generate a code comment based on the code, please do not output "No relevant sentence identified in the issue report."\n' \
           f'DO NOT OUTPUT "No relevant sentence identified in the issue report."!!!\n' \
           f'Code Snippet:\n{code}\n\n'\
           f'Issue Report:\n{issue}\n\n' \
           f'DO NOT OUTPUT "No relevant sentence identified in the issue report."!!!\n' \
           f'Ouput format:\n'\
           f'Functionality: functionality_comment_content\n'\
           f'Concept: concept_comment_content\n'\
           f'Directive: directive_comment_content\n'\
           f'Rationale: rationale_comment_content\n'\
           f'Implication: implication_comment_content\n'\

def post_process(comment, code_indent):
    lines = comment.split('\n')
    keywords = {}
    current_keyword = None
    
    for line in lines:
        if ':' in line:
            keyword, content = line.split(':', 1)
            keyword = keyword.strip()
            content = content.strip()
            if content != '':
                current_keyword = keyword
                keywords[keyword] = content
            else:
                current_keyword = None
        elif current_keyword is not None:
            keywords[current_keyword] += ' ' + line.strip()

    result = " " * code_indent + "/**\n"
    for keyword, content in keywords.items():
        if content == "No relevant sentence identified in the issue report.": continue
        result += " " * code_indent + " * " + keyword + ": \n" + " " * code_indent + " * " + content + "\n"
    result += " " * code_indent + " */"
    return result

@app.route('/', methods=['POST'])
def api():
    # data = request.get_json()
    data = request.data
    data = json.loads(data)
    print("data:", data)
    inp_code = data['code']
    config = data['config']
    issue_path = data['issue_path']
    specific_issue = data['specific_issue']
    code_indent = len(inp_code) - len(inp_code.lstrip())
    print("input_code:\n", inp_code.strip())
    print("input_config:\n", config)

    # 1. retrieve issue
    if specific_issue == "":
        issue = search_issue(inp_code, issue_path)
    else: issue = specific_issue

    # 2. call backend model
    if issue == "error":
        return jsonify({
            "input": inp_code,
            "output": "Failed to process the file at the specified path of code-issue pairs"
        })

    if issue != "none":
        model_input = icom_prompt(inp_code, issue, config)
    else:
        model_input = codePrompt(inp_code)
    print("model_input:\n", model_input)
    model_raw_output = completions_with_backoff(model_input, temperature=0.8)
    model_raw_output = model_raw_output['choices'][0]['message']['content']

    # 3. post process 
    model_output = post_process(model_raw_output, code_indent) 

    return jsonify({
        "input": model_input,
        "output": model_output
    })

if __name__ == '__main__':
    # localhost:8000
    app.run(debug=True, port=8000)