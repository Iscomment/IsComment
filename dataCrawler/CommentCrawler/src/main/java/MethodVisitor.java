import org.eclipse.jdt.core.dom.*;
import org.eclipse.jgit.diff.Edit;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class MethodVisitor extends ASTVisitor {
    public List<ChangedMethod> changedMethods = new ArrayList<>();
    public String fileContent;
    public String prefileContent;
    public String filename;
    public List<Edit> edits;

    public MethodVisitor(String filename, String fileContent, String prefileContent, List<Edit>edits){
        this.filename = filename;
        this.fileContent = fileContent;
        this.prefileContent = prefileContent;
        this.edits = edits;
    }

    public boolean visit(TypeDeclaration node){
        MethodDeclaration[] methodDeclarations = node.getMethods();
        for (MethodDeclaration methodDeclaration : methodDeclarations) {
            ChangedMethod method = createMethod(methodDeclaration, NameResolver.getFullName(node));
            if(method!=null){
                changedMethods.add(method);
            }
        }
        return false;
    }

    public String getContent(String content,int start,int end){
        StringBuilder result = new StringBuilder();
        String[]lines = content.split("\n");
        for(int i=start;i<end;i++){
            result.append(lines[i]);
        }
        return result.toString();
    }


    public ChangedMethod createMethod(MethodDeclaration node,String belongTo){
        if(node.getBody() == null) return null;
        if(node.getJavadoc() == null) return null;

        String comment = node.getJavadoc().toString();
        int commentStart = fileContent.substring(0,node.getJavadoc().getStartPosition()).split("\\n").length;
        int commentEnd = fileContent.substring(0,node.getJavadoc().getStartPosition()+node.getJavadoc().getLength()).split("\\n").length;

        String content = fileContent.substring(node.getJavadoc().getStartPosition()+node.getJavadoc().getLength(),node.getStartPosition()+node.getLength()).trim();
        int startline = commentEnd+1;
        int endline = fileContent.substring(0,node.getBody().getStartPosition()+node.getBody().getLength()).split("\\n").length;

        String name = node.getName().getFullyQualifiedName();
        String params = String.join(", ", (List<String>) node.parameters().stream().map(n -> {
            SingleVariableDeclaration param = (SingleVariableDeclaration) n;
            return (Modifier.isFinal(param.getModifiers()) ? "final " : "") + param.getType().toString() + " " + param.getName().getFullyQualifiedName();
        }).collect(Collectors.toList()));
        String fullName = belongTo + "." + name + "( " + params + " )";

        List<String> changeTypes = new ArrayList<>();

        boolean commentChanged = false;
        for(Edit edit: edits){
            if(edit.getBeginB()>=commentEnd){
                continue;
            }
            if(edit.getEndB()<commentStart){
                continue;
            }
            if(edit.getType().equals("DELETE")){
                continue;
            }
            if(edit.getType().equals("REPLACE")){
                continue;
            }
            commentChanged = true;
        }
        if(commentChanged==false) return null;

        List<DiffContent> diffContents = new ArrayList<>();
        boolean codeChanged =false;
        for(Edit edit: edits){
            if(edit.getBeginB()>=endline){
                continue;
            }
            if(edit.getEndB()<startline){
                continue;
            }
            String edit_type = edit.getType().toString();
            changeTypes.add(edit_type);

            if(edit_type.equals("INSERT")){
                diffContents.add(new DiffContent(edit_type,"",getContent(fileContent,Math.max(edit.getBeginB(),startline-1),Math.min(edit.getEndB(),endline))));
            }else if(edit_type.equals("DELETE")){
                diffContents.add(new DiffContent(edit_type,getContent(prefileContent,edit.getBeginA(),edit.getEndA()),""));
            }else if(edit_type.equals("REPLACE")){
                DiffContent diff = new DiffContent(edit_type,getContent(prefileContent,edit.getBeginA(),edit.getEndA()),getContent(fileContent,Math.max(edit.getBeginB(),startline-1),Math.min(edit.getEndB(),endline)));
                diffContents.add(diff);
            }
            codeChanged =true;
        }
        if(codeChanged==false) return null;
        ChangedMethod info = new ChangedMethod(name, fullName ,filename,content,comment,startline,endline,commentStart,commentEnd,changeTypes,diffContents);
        return info;
    }
}
