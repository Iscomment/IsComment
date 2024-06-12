import java.util.List;

public class ChangedMethod {
    public String name;
    public String fullname;
    public String fileName;
    public String content;
    public String comment;
    public int start;
    public int end;
    public int commentStart;
    public int commentEnd;
    public List<String> changeTypes; //insert or replace or delete
    public List<DiffContent> diffContents;

    public ChangedMethod(String name,String fullname,String fileName,String content,String comment,int start,int end,
                         int commentStart,int commentEnd,List<String> changeTypes,List<DiffContent> diffContents){
        this.name = name;
        this.fullname = fullname;
        this.fileName = fileName;
        this.content = content;
        this.comment = comment;
        this.start = start;
        this.end = end;
        this.commentStart = commentStart;
        this.commentEnd = commentEnd;
        this.changeTypes = changeTypes;
        this.diffContents = diffContents;
    }
}
