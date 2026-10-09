package art.lazying.lazyedit;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import org.json.JSONObject;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.*;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/** Native HTTPS client. Session material is encrypted with this app's Keystore key. */
final class StudioApi {
    static final String ORIGIN = "https://edit.lazying.art";
    private final Context context;
    private JSONObject identity;
    static final class Failure extends IOException {
        final int status;
        final boolean rejected;
        Failure(String message, int status, boolean rejected) { super(message); this.status=status; this.rejected=rejected; }
    }
    static final class Reply {
        final int status;
        final byte[] bytes;
        final Map<String,List<String>> headers;
        Reply(int status, byte[] bytes, Map<String,List<String>> headers) { this.status=status; this.bytes=bytes; this.headers=headers; }
        JSONObject json() throws Exception { return new JSONObject(new String(bytes, StandardCharsets.UTF_8)); }
    }
    StudioApi(Context context) {
        this.context=context.getApplicationContext();
        try {
            JSONObject stored=new JSONObject(readSecret());
            if(stored.optLong("expires")>System.currentTimeMillis()) identity=stored;
        } catch(Exception ignored) {}
    }
    private String publishingScope;
    private boolean publishingAllowed;
    private boolean agentAllowed;
    boolean agentEnabled() { return scope().equals(publishingScope) && agentAllowed; }
    boolean publishingEnabled() { return scope().equals(publishingScope) && publishingAllowed; }
    boolean signedIn() { return identity!=null; }
    String mode() { return identity==null?"owner":identity.optString("mode","owner"); }
    String username() { return identity==null?"":identity.optString("username"); }
    String scope() { return username().replaceAll("[^a-zA-Z0-9_-]","_")+"-"+mode(); }
    File file(String name) { return new File(context.getFilesDir(),scope()+"-"+name); }
    String cookie() {
        if(identity==null)return "";
        String value=identity.optString("studio").isEmpty()?"":"__Host-studio="+identity.optString("studio");
        if(!identity.optString("hosted").isEmpty())value+=(value.isEmpty()?"":"; ")+"__Host-hosted="+identity.optString("hosted");
        return value;
    }
    static URL url(String path) throws Exception {
        URL url=new URL(new URL(ORIGIN),path);
        if(!url.getProtocol().equals("https")||!url.getHost().equals("edit.lazying.art")||url.getUserInfo()!=null||(url.getPort()!=-1&&url.getPort()!=443))throw new IOException("This link does not belong to your Studio.");
        return url;
    }
    private SecretKey key() throws Exception {
        KeyStore store=KeyStore.getInstance("AndroidKeyStore");store.load(null);
        String alias="lazyedit-native-session";
        if(!store.containsAlias(alias)) {
            KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
            generator.init(new KeyGenParameterSpec.Builder(alias,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());generator.generateKey();
        }
        return (SecretKey)store.getKey(alias,null);
    }
    private File secretFile() { return new File(context.getFilesDir(),"session.encrypted"); }
    private String readSecret() throws Exception {
        JSONObject data=new JSONObject(readFile(secretFile()));
        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.DECRYPT_MODE,key(),new GCMParameterSpec(128,Base64.decode(data.getString("iv"),Base64.NO_WRAP)));
        return new String(cipher.doFinal(Base64.decode(data.getString("data"),Base64.NO_WRAP)),StandardCharsets.UTF_8);
    }
    private void save() throws Exception {
        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.ENCRYPT_MODE,key());
        JSONObject value=new JSONObject().put("iv",Base64.encodeToString(cipher.getIV(),Base64.NO_WRAP)).put("data",Base64.encodeToString(cipher.doFinal(identity.toString().getBytes(StandardCharsets.UTF_8)),Base64.NO_WRAP));
        writeFile(secretFile(),value.toString());
    }
    static String readFile(File file) throws IOException { try(InputStream in=new FileInputStream(file)) { return new String(read(in,200000),StandardCharsets.UTF_8); } }
    static void writeFile(File file,String data) throws IOException {
        File stage=new File(file.getParentFile(),file.getName()+".tmp");
        try(FileOutputStream out=new FileOutputStream(stage)) { out.write(data.getBytes(StandardCharsets.UTF_8));out.getFD().sync(); }
        if(!stage.renameTo(file))throw new IOException("Could not save your local state.");
    }
    private static byte[] read(InputStream input,int max) throws IOException {
        if(input==null)return new byte[0];
        try(InputStream in=input;ByteArrayOutputStream out=new ByteArrayOutputStream()) {
            byte[] buffer=new byte[8192];int size;
            while((size=in.read(buffer))!=-1) { if(out.size()+size>max)throw new IOException("Studio response is too large.");out.write(buffer,0,size); }
            return out.toByteArray();
        }
    }
    Reply send(String path,String method,byte[] data,String contentType,String key,String currentCookie,boolean entry) throws Exception {
        HttpURLConnection connection=(HttpURLConnection)url(path).openConnection();
        connection.setInstanceFollowRedirects(false);connection.setConnectTimeout(20000);connection.setReadTimeout(120000);connection.setRequestMethod(method);
        connection.setRequestProperty("Origin",ORIGIN);connection.setRequestProperty("Accept","application/json");
        if(!currentCookie.isEmpty())connection.setRequestProperty("Cookie",currentCookie);
        if(key!=null)connection.setRequestProperty("Idempotency-Key",key);
        if(contentType.startsWith("application/octet-stream:")) { connection.setRequestProperty("Upload-Offset",contentType.substring(contentType.indexOf(':')+1));contentType="application/octet-stream"; }
        try {
            if(data!=null) { connection.setDoOutput(true);connection.setRequestProperty("Content-Type",contentType);connection.setFixedLengthStreamingMode(data.length);try(OutputStream out=connection.getOutputStream()) { out.write(data); } }
            int status=connection.getResponseCode();
            Reply reply=new Reply(status,read(status>=400?connection.getErrorStream():connection.getInputStream(),8*1024*1024),connection.getHeaderFields());
            if((status<200||status>=300)&&!(entry&&status==303)) {
                JSONObject value;try { value=reply.json(); } catch(Exception ignored) { value=new JSONObject(); }
                Object error=value.opt("error");String message=error instanceof JSONObject?((JSONObject)error).optString("message",((JSONObject)error).optString("code","Studio request failed")):value.optString("error","Studio request failed ("+status+").");
                if(status==401)message="Your session expired. Sign in again.";
                throw new Failure(message,status,value.optString("submissionState").equals("rejected"));
            }
            return reply;
        } finally { connection.disconnect(); }
    }
    private void absorb(Reply reply) throws Exception {
        for(Map.Entry<String,List<String>> entry:reply.headers.entrySet())if(entry.getKey()!=null&&entry.getKey().equalsIgnoreCase("set-cookie")) {
            for(String header:entry.getValue()) for(HttpCookie cookie:HttpCookie.parse(header)) {
                if(cookie.getName().equals("__Host-studio"))identity.put("studio",cookie.getMaxAge()==0?"":cookie.getValue());
                if(cookie.getName().equals("__Host-hosted"))identity.put("hosted",cookie.getMaxAge()==0?"":cookie.getValue());
            }
        }
        identity.put("expires",System.currentTimeMillis()+43200000);save();
    }
    JSONObject json(String path) throws Exception {
        String original=cookie();
        for(int attempt=0;;attempt++) {
            try { Reply reply=send(path,"GET",null,"application/json",null,original,false);if(!cookie().equals(original))throw new IOException("Workspace changed.");JSONObject result=reply.json();if(path.equals("/auth/me")){publishingScope=scope();agentAllowed=result.optJSONObject("capabilities")!=null&&result.getJSONObject("capabilities").optBoolean("agentChat");publishingAllowed=result.optJSONObject("capabilities")!=null?result.getJSONObject("capabilities").optBoolean("publishing"):mode().equals("owner")&&result.optJSONArray("scopes")!=null&&result.getJSONArray("scopes").toString().contains("publication.publish");}return result; }
            catch(Failure failure) { if(attempt>=2||!Arrays.asList(429,502,503,504).contains(failure.status))throw failure;Thread.sleep((attempt+1)*1000L); }
        }
    }
    JSONObject post(String path,JSONObject body) throws Exception { return post(path,body,null); }
    JSONObject post(String path,JSONObject body,String key) throws Exception { return send(path,"POST",body.toString().getBytes(StandardCharsets.UTF_8),"application/json",key,cookie(),false).json(); }
    void login(String username,String password,boolean workspace,String invitation) throws Exception {
        JSONObject body=new JSONObject().put("username",username).put("password",password);
        if(invitation!=null)body.put("invitation",invitation);
        Reply reply=send(workspace?(invitation==null?"/accounts/login":"/accounts/register"):"/auth/login","POST",body.toString().getBytes(StandardCharsets.UTF_8),"application/json",null,"",false);
        identity=new JSONObject().put("username",username).put("mode",workspace?"workspace":"owner");absorb(reply);
        if(workspace)enterWorkspace();
    }
    void enterWorkspace() throws Exception {
        for(int attempt=0;attempt<36;attempt++) {
            String state=json("/accounts/account").optString("status");
            if(state.equals("ready"))break;
            if(state.equals("failed")||state.equals("suspended"))throw new IOException("Workspace could not start. Contact the administrator.");
            Thread.sleep(5000);
        }
        String url=post("/accounts/enter",new JSONObject()).getString("url");
        Reply reply=send(url,"GET",null,"application/json",null,cookie(),true);
        if(reply.status!=303)throw new IOException("Workspace entry was incomplete.");absorb(reply);
    }
    void oauthRedeem(String ticket,String verifier) throws Exception {
        JSONObject body=new JSONObject().put("ticket",ticket).put("verifier",verifier);
        Reply reply=send("/accounts/oauth/redeem","POST",body.toString().getBytes(StandardCharsets.UTF_8),"application/json",null,cookie(),false);
        String username=reply.json().getString("username");
        identity=new JSONObject().put("username",username).put("mode","workspace");absorb(reply);enterWorkspace();
    }
    void switchMode() throws Exception {
        boolean workspace=!mode().equals("workspace");
        Reply reply=send(workspace?"/accounts/docker":"/accounts/owner","POST","{}".getBytes(StandardCharsets.UTF_8),"application/json",null,cookie(),false);
        identity.put("mode",workspace?"workspace":"owner");absorb(reply);if(workspace)enterWorkspace();
    }
    void logout() throws Exception {
        post("/auth/logout",new JSONObject());
        clear();
    }
    void clear() { identity=null;publishingScope=null;publishingAllowed=false;secretFile().delete(); }
    long chunk(String id,long offset,byte[] bytes) throws Exception { return send("/v1/studio/upload-part?uploadId="+id,"PUT",bytes,"application/octet-stream:"+offset,null,cookie(),false).json().getLong("offset"); }
}
