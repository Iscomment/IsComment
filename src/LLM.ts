// import fetch from 'axios';
import * as vscode from 'vscode';
import { fetch } from 'undici';
import {keys, url} from './gpt35_keys';

async function pyBackend(inp_code: string, config_dict: { [x: string]: boolean | undefined; }, backendURL: string | null | undefined, issue_path: string | null | undefined, specific_issue: string | null | undefined): Promise<{ input?: string, output?: string } | null | undefined>{
    var data = {
        "code": inp_code,
        "issue_path":issue_path,
        "specific_issue":specific_issue,
        "config": config_dict
    }
    if (backendURL == null || backendURL == undefined) {
        vscode.window.showErrorMessage("Backend URL is not set");
        return null;
    }
    const response = await fetch(backendURL, { 
        method: 'POST', 
        body: JSON.stringify(data)
    });
    return await response.json() as { input?: string, output?: string } | null | undefined;
}


async function gpt35(inp: string, temperature: number = 0.01, max_tokens: number = 512): Promise<any> {
    const API_URL = url;
    const headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + keys
    }
    const data = {
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: inp}],
        temperature: temperature,
        max_tokens: max_tokens
    }
    const response = await fetch(API_URL, { 
        method: 'POST', 
        headers: headers, 
        body: JSON.stringify(data) 
    });
    return await response.json();
};

export {gpt35, pyBackend};