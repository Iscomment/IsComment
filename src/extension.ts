import * as vscode from 'vscode';
import {
	DocumentFilter,
	LanguageClient,
	LanguageClientOptions,
	ServerOptions,
	TransportKind,
	integer
} from 'vscode-languageclient/node';
import { TemplateKey, templates } from './configTemplates';
import { readFile } from 'fs';
import { homedir } from 'os';
import * as path from 'path';
import { fetch } from 'undici';

import {gpt35, pyBackend} from './LLM';


async function toGPT35(inp_code: string, config_dict: { [x: string]: boolean | undefined; }){
	// construct prompt string
	var promptString: string = 'Please generate a comment given the following settings: \n';
	for (var key in config_dict) {
		promptString = promptString + key + ': ' + config_dict[key] + '\n';
	}
	promptString = promptString + 'Input code:\n';
	promptString = promptString + inp_code;

	const response = await gpt35(promptString);
	return {"input": promptString, "output": response.choices[0].message.content};
}

async function toBackend(inp_code: string, config_dict: { [x: string]: boolean | undefined; }, backendURL: string | null | undefined, 
		issue_path: string | null | undefined, specific_issue: string | null | undefined) {
	const response: { input?: string, output?: string } | null | undefined = await pyBackend(inp_code, config_dict, backendURL, issue_path, specific_issue);
	if (response == undefined || response == null) {
		vscode.window.showErrorMessage("Backend response is undefined");
		return {"input": "", "output": ""};
	}
	if (response.output == "Failed to process the file at the specified path of code-issue pairs") {
		vscode.window.showErrorMessage("Error: Failed to process the file at the specified path of code-issue pairs");
		return {"input": "", "output": ""};
	}
	var inp = response.input || "";
	var out = response.output || "";
	return {"input": inp, "output": out};
}

export async function activate(ctx:vscode.ExtensionContext) {
	vscode.commands.registerCommand('extension.addComments', () => {

		// get the input code
		if (!vscode.window.activeTextEditor) return;
		var selection = vscode.window.activeTextEditor.selection;
		var selectedText = vscode.window.activeTextEditor.document.getText(selection);
		var inp_code = selectedText;

		// get the configuration
		var config = vscode.workspace.getConfiguration('commentType');
		var config_keys = ['Functionality', 'Concept', 'Directive', 'Rationale', "Implication"];
		var config_dict: Record<string, boolean | undefined> = {};
		for (var i = 0; i < config_keys.length; i++) {
			config_dict[config_keys[i]] = config.get(config_keys[i]);
		}
		var backend_config = vscode.workspace.getConfiguration("commentDebug");
		var useModel = backend_config.get("ModelChoice");
		var backendURL: string | null | undefined = backend_config.get("customBackendURL");
		var issue_config = vscode.workspace.getConfiguration("IssueConfig");
		var issue_path: string | null | undefined = issue_config.get("Path");
		var specific_issue: string | null | undefined = issue_config.get("SpecificIssue");

		// call the llm or the backend
		if (useModel == "ChatGPT") {
			useModel
			toBackend(inp_code, config_dict, backendURL, issue_path, specific_issue).then((inp_out_dict: {[x:string]: string | undefined}) => {
				processOutput(inp_out_dict, selection);
			}
			);
		}
		else if (useModel == "Claude") {
			// to be implemented
			toBackend(inp_code, config_dict, backendURL, issue_path, specific_issue).then((inp_out_dict: {[x:string]: string | undefined}) => {
				processOutput(inp_out_dict, selection);
			}
			);
		}
		else {
			vscode.window.showInformationMessage("No model available: " + useModel);
		}
	});
}

function processOutput(inp_out_dict: {[x:string]: string | undefined}, selection:vscode.Selection) {
	var inp_with_out = '/* input:\n' + inp_out_dict['input'] + '\n\noutput:\n' + inp_out_dict['output'] + ' */';
	var only_out = ''+inp_out_dict['output'];
	var output_config = vscode.workspace.getConfiguration("commentDebug");

	var textToInsert = output_config.get("InputShown") ? inp_with_out : only_out;
	var startLine = selection.start.line - 1;
	insertContent(startLine, textToInsert, selection);
}


// insertContent is copied from the original "comment-vscode"
function insertContent(startLine:integer, textToInsert:string, selection:vscode.Selection) {
	if (!vscode.window.activeTextEditor) return;
	vscode.window.activeTextEditor.edit((editBuilder: vscode.TextEditorEdit) => {
		if (startLine < 0) {
			startLine = 0;
			textToInsert = textToInsert + '\n';
		}
		//Check if there is any text on startLine. If there is, add a new line at the end
		if (!vscode.window.activeTextEditor) return;
		var lastCharIndex = vscode.window.activeTextEditor.document.lineAt(startLine).text.length;
		var pos:vscode.Position;
		if ((lastCharIndex > 0) && (startLine !=0)) {
			pos = new vscode.Position(startLine, lastCharIndex);
			textToInsert = '\n' + textToInsert; 	
		}
		else {
			pos = new vscode.Position(startLine, 0);
		}
		var line:string = vscode.window.activeTextEditor.document.lineAt(selection.start.line).text;
		var firstNonWhiteSpace :number = vscode.window.activeTextEditor.document.lineAt(selection.start.line).firstNonWhitespaceCharacterIndex;
		var numIndent : number = 0;
		var stringToIndent: string = '';
		for (var i = 0; i < firstNonWhiteSpace; i++) {
			if (line.charAt(i) == '\t') {
				stringToIndent = stringToIndent + '\t';
			}
			else if (line.charAt(i) == ' ') {
				stringToIndent = stringToIndent + ' ';
			}
		}					
		editBuilder.insert(pos, textToInsert);
	}).then(() => {		
	});
}