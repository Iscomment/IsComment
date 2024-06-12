import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.diff.DiffEntry;
import org.eclipse.jgit.diff.DiffFormatter;
import org.eclipse.jgit.diff.Edit;
import org.eclipse.jgit.diff.RawTextComparator;
import org.eclipse.jgit.internal.storage.file.FileRepository;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.ObjectLoader;
import org.eclipse.jgit.lib.Repository;
import org.eclipse.jgit.patch.FileHeader;
import org.eclipse.jgit.patch.HunkHeader;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.revwalk.RevWalk;
import org.eclipse.jgit.treewalk.TreeWalk;
import org.eclipse.jgit.treewalk.filter.PathFilter;
import org.eclipse.jgit.util.io.DisabledOutputStream;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class main {

    public static String getIssueId(String project, String commitMessage,List<String>issueTags){
        for(String tag:issueTags){
            String pattern = tag + "-[0-9]+";
            Pattern r = Pattern.compile(pattern);
            Matcher m = r.matcher(commitMessage);
            if (m.find( )) {
                return m.group(0);
            }
        }
        return null;
    }

    public static String getFileFromCommit(Repository repository, ObjectId commitId, String filePath){
        String result = "";
        try(TreeWalk treeWalk = new TreeWalk(repository)){
            treeWalk.reset(repository.resolve(commitId.getName()+"^{tree}"));
            treeWalk.setFilter(PathFilter.create(filePath));
            treeWalk.setRecursive(true);
            if(treeWalk.next()){
                ObjectId objectId = treeWalk.getObjectId(0);
                ObjectLoader loader = repository.open(objectId);
                result = new String(loader.getBytes());
            }
        }catch (Exception e){
            System.out.println(" error + " + commitId.getName() + "\n");
            System.out.println(e.getMessage());
        }
        return result;
    }


    public static void process(String gitPath,String repoPath,String project,List<String>issueTags){
        try {
            Repository repository = new FileRepository(gitPath);
            Git git = new Git(repository);
            Iterator<RevCommit> commits = git.log().call().iterator();

            int total = 0;
            while(commits.hasNext()){
                total++;
                commits.next();
            }

            System.out.println(total);

            int cnt= 0;
            commits = git.log().call().iterator();
            while(commits.hasNext()){
                RevCommit cur = commits.next();
                System.out.println(cur.getName());
                cnt++;
                RevWalk rw = new RevWalk(repository);

                String message = cur.getFullMessage();
                String issueId = getIssueId(project, message,issueTags);
                if(issueId == null) continue;

                List<ChangedMethod> results = new ArrayList<>();

                RevCommit par = rw.parseCommit(cur.getParent(0).getId());
                DiffFormatter df = new DiffFormatter(DisabledOutputStream.INSTANCE);
                df.setRepository(repository);
                df.setDiffComparator(RawTextComparator.DEFAULT);
                df.setDetectRenames(true);
                List<DiffEntry> diffs = df.scan(par.getTree(), cur.getTree());

                Set<String> filenames = new HashSet<>();
                HashMap<String,List<Edit>> file2edits = new HashMap<>();
                for(DiffEntry diff: diffs) {
                    if(diff.getChangeType().equals(DiffEntry.ChangeType.DELETE))continue;
                    if(diff.getChangeType().equals(DiffEntry.ChangeType.COPY))continue;
                    if(diff.getChangeType().equals(DiffEntry.ChangeType.RENAME))continue;

                    String fileName = diff.getNewPath();
                    if (!fileName.endsWith(".java")) continue;
                    if(fileName.contains("test") || fileName.contains("Test"))continue;
                    filenames.add(fileName);

                    List<Edit> edits = new ArrayList<>();
                    try (DiffFormatter formatter = new DiffFormatter(System.out)) {
                        formatter.setRepository(repository);
                        FileHeader fileheader = formatter.toFileHeader(diff);
                        List<HunkHeader>hunks = (List<HunkHeader>)fileheader.getHunks();
                        for(HunkHeader hunkHeader:hunks){
                            edits.addAll(hunkHeader.toEditList());
                        }
                    }

                    if(file2edits.containsKey(fileName)){
                        file2edits.get(fileName).addAll(edits);
                    }else{
                        file2edits.put(fileName,edits);
                    }
                }

                if(filenames.size()>10) continue;  //Too much change

                for(String fileName:filenames){
                    System.out.println(fileName);

                    String curfile = getFileFromCommit(repository,cur.getId(),fileName);
                    String prefile = getFileFromCommit(repository,par.getId(),fileName);
                    ASTParser parser = ASTParser.newParser(AST.JLS10);
                    parser.setSource(curfile.toCharArray());
                    parser.setKind(ASTParser.K_COMPILATION_UNIT);
                    parser.setResolveBindings(true);
                    parser.setBindingsRecovery(true);
                    parser.setEnvironment(null, new String[]{repoPath}, new String[]{"utf-8"}, true);

                    ASTVisitor visitor=new MethodVisitor(fileName,curfile,prefile,file2edits.get(fileName));
                    CompilationUnit unit=(CompilationUnit)parser.createAST(null);
                    unit.accept(visitor);
                    results.addAll(((MethodVisitor) visitor).changedMethods);

                    for(ChangedMethod m:results){
                        JSONObject info = new JSONObject();
                        info.put("commitId",cur.getName());
                        info.put("name",m.name);// method name
                        info.put("fullname",m.fullname);
                        info.put("fileName",m.fileName);
                        info.put("content",m.content); // method body
                        info.put("ori_comment",m.comment);
                        info.put("issueId",issueId);
                        info.put("diffs",m.diffContents);
                        info.put("changeTypes",m.changeTypes);
                        info.put("commitTime",cur.getCommitTime());
                        ReadWriteUtil.writeFileAppend("D:\\Data\\"+project+".json", JSON.toJSONString(info)+"\n");
                    }
                }
            }
        }catch (Exception e){
            e.printStackTrace();
        }
    }


    public static void main(String args[]) {

        String project = "ambari";
        String git_path = "D:\\ApacheProjects\\ambari\\.git";
        String repo_path = "D:\\ApacheProjects\\ambari";
        List<String> issueTag = Arrays.asList(new String []{"AMBARI"});
        process(git_path,repo_path,project,issueTag);

//        project = "camel";
//        gitPath =  "D:\\ApacheProjects\\camel\\.git";
//        repoPath = "D:\\ApacheProjects\\camel";
//        issueTags = Arrays.asList(new String []{"CAMEL"});
//        process(gitPath,repoPath,project,issueTags);

//        project = "derby";
//        gitPath = "D:\\ApacheProjects\\derby\\.git";
//        repoPath = "D:\\ApacheProjects\\derby";
//        issueTags = Arrays.asList(new String []{"DERBY"});
//        process(gitPath,repoPath,project,issueTags);

//        project = "flink";
//        gitPath = "D:\\ApacheProjects\\flink\\.git";
//        repoPath = "D:\\ApacheProjects\\flink";
//        issueTags = Arrays.asList(new String []{"FLINK"});
//        process(gitPath,repoPath,project,issueTags);

//        project = "hadoop";
//        gitPath = "D:\\ApacheProjects\\hadoop\\.git";
//        repoPath = "D:\\ApacheProjects\\hadoop";
//        issueTags = Arrays.asList(new String []{"HADOOP","YARN","MAPREDUCE","HDFS"});
//        process(gitPath,repoPath,project,issueTags);

//        project = "hbase";
//        gitPath = "D:\\ApacheProjects\\hbase\\.git";
//        repoPath = "D:\\ApacheProjects\\hbase";
//        issueTags = Arrays.asList(new String []{"HBASE"});
//        process(gitPath,repoPath,project,issueTags);

//        String project = "jackrabbit";
//        String git_path = "D:\\ApacheProjects\\jackrabbit\\.git";
//        String repo_path = "D:\\ApacheProjects\\jackrabbit";
//        List<String> issueTag = Arrays.asList(new String []{"JCR"});
//        process(git_path,repo_path,project,issueTag);

//        String gitPath = "D:\\ApacheProjects\\lucene\\.git";
//        String repoPath = "D:\\ApacheProjects\\lucene";
//        String project = "lucene";
//        List<String> issueTags = Arrays.asList(new String []{"LUCENE","SOLR"});
//        process(gitPath,repoPath,project,issueTags);

//        String project = "pdfbox";
//        String git_path = "D:\\ApacheProjects\\pdfbox\\.git";
//        String repo_path = "D:\\ApacheProjects\\pdfbox";
//        List<String> issueTag = Arrays.asList(new String []{"PDFBOX"});
//        process(git_path,repo_path,project,issueTag);

//        String project = "wicket";
//        String git_path = "D:\\ApacheProjects\\wicket\\.git";
//        String repo_path = "D:\\ApacheProjects\\wicket";
//        List<String> issueTag = Arrays.asList(new String []{"WICKET"});
//        process(git_path,repo_path,project,issueTag);
    }
}
