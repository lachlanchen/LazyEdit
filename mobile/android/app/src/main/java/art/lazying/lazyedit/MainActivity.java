package art.lazying.lazyedit;

import android.app.AlertDialog;
import android.content.*;
import android.database.Cursor;
import android.graphics.Color;
import android.net.Uri;
import android.os.*;
import android.provider.OpenableColumns;
import android.text.InputType;
import android.view.*;
import android.webkit.*;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.splashscreen.SplashScreen;
import org.json.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;

/** Native Studio screens; the web editor is an optional secondary tool. */
public class MainActivity extends AppCompatActivity {
    private StudioApi api;
    private final ExecutorService worker=Executors.newFixedThreadPool(2);
    private final Handler ui=new Handler(Looper.getMainLooper());
    private LinearLayout root,content;
    private TextView message;
    private int screen=0;
    private boolean busy=false;
    private boolean foreground=false;
    private volatile boolean uploading=false;
    private WebView editor;
    private VideoView player;
    private String oauthVerifier;
    private StudioBilling billing;
    private final Runnable attentionPoll=()->{ if(foreground&&api.signedIn()) { if(screen!=2)checkAttention();ui.postDelayed(this.attentionPoll,30000); } };
    private final Runnable poll=()->{if(foreground&&screen==2&&!busy&&api.signedIn())activity();};
    private interface Work<T> { T run() throws Exception; }
    private interface Result<T> { void accept(T value) throws Exception; }
    boolean isWorking() { return busy; }
    private void enableButtons(View view,boolean enabled) {
        if(view instanceof Button)view.setEnabled(enabled||"pause-upload".equals(view.getTag()));
        if(view instanceof ViewGroup)for(int i=0;i<((ViewGroup)view).getChildCount();i++)enableButtons(((ViewGroup)view).getChildAt(i),enabled);
    }
    @Override public void onCreate(Bundle state) {
        SplashScreen.installSplashScreen(this);super.onCreate(state);api=new StudioApi(this);
        if(api.signedIn()&&api.scope().equals(getIntent().getStringExtra("attentionScope")))screen=2;
        show();
    }
    private String tr(String value) { return StudioStrings.text(this,value); }
    private int dp(int value) { return Math.round(value*getResources().getDisplayMetrics().density); }
    private LinearLayout column() { LinearLayout value=new LinearLayout(this);value.setOrientation(LinearLayout.VERTICAL);return value; }
    private void frame(String title,boolean tabs) {
        if(billing!=null){billing.close();billing=null;}
        ui.removeCallbacks(poll);if(player!=null){player.stopPlayback();player=null;}if(editor!=null){editor.destroy();editor=null;}
        root=column();root.setPadding(dp(20),dp(12),dp(20),0);root.setBackgroundColor(Color.rgb(246,248,252));root.setLayoutDirection(StudioStrings.language(this).equals("ar")?View.LAYOUT_DIRECTION_RTL:View.LAYOUT_DIRECTION_LTR);
        root.setOnApplyWindowInsetsListener((v,insets)->{v.setPadding(dp(20),insets.getSystemWindowInsetTop()+dp(12),dp(20),insets.getSystemWindowInsetBottom());return insets;});
        TextView heading=new TextView(this);heading.setText(tr(title));heading.setTextSize(28);heading.setTextColor(Color.rgb(24,45,78));root.addView(heading);
        message=new TextView(this) { @Override public void setText(CharSequence value,BufferType type) { super.setText(value instanceof String?tr((String)value):value,type); } };message.setTextSize(14);message.setTextColor(Color.rgb(125,67,25));message.setPadding(0,dp(8),0,dp(8));root.addView(message);
        ScrollView scroll=new ScrollView(this);content=column();scroll.addView(content);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        if(tabs){LinearLayout nav=new LinearLayout(this);String[] labels={"Studio","Upload","Activity","Account"};for(int i=0;i<labels.length;i++){final int index=i;Button button=new Button(this);button.setText(tr(labels[i]));button.setTextSize(12);button.setOnClickListener(v->{if(busy)return;screen=index;show();});nav.addView(button,new LinearLayout.LayoutParams(0,dp(60),1));}root.addView(nav);}
        setContentView(root);
    }
    private TextView text(String value) { TextView view=new TextView(this);view.setText(tr(value));view.setTextSize(16);view.setPadding(0,dp(10),0,dp(10));content.addView(view);return view; }
    private Button button(String label,Runnable action) { Button value=new Button(this);value.setText(tr(label));value.setAllCaps(false);value.setOnClickListener(v->{if(!busy)action.run();});content.addView(value);return value; }
    private EditText field(String hint,String value,boolean multi) { EditText input=new EditText(this);input.setHint(tr(hint));input.setText(value);input.setSingleLine(!multi);if(multi){input.setMinLines(3);input.setMaxLines(8);input.setGravity(Gravity.TOP);}content.addView(input);return input; }
    private CheckBox check(String label,boolean checked) { CheckBox box=new CheckBox(this);box.setText(tr(label));box.setChecked(checked);content.addView(box);return box; }
    private Spinner choice(String label,String[] values,String selected) { text(label);Spinner spinner=new Spinner(this);spinner.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,values));for(int i=0;i<values.length;i++)if(values[i].equals(selected))spinner.setSelection(i);content.addView(spinner);return spinner; }
    private void error(Exception failure) {
        if(isFinishing())return;
        if(failure instanceof StudioApi.Failure&&((StudioApi.Failure)failure).status==401){api.clear();show();}
        message.setText(failure.getMessage()==null?"Studio is temporarily unavailable.":failure.getMessage());
    }
    private <T> void task(String progress,Work<T> work,Result<T> result) {
        if(busy)return;busy=true;message.setText(progress);enableButtons(root,false);
        worker.execute(()->{try{T value=work.run();ui.post(()->{busy=false;if(isDestroyed())return;enableButtons(root,true);try{result.accept(value);}catch(Exception e){error(e);}});}catch(Exception e){ui.post(()->{busy=false;if(!isDestroyed()){enableButtons(root,true);error(e);}});}});
    }
    private void show() {
        if(!api.signedIn()){login();return;}
        if(screen==1)uploadScreen();else if(screen==2)activity();else if(screen==3)account();else library(false);
    }
    private void chooseLanguage() {
        if(busy||uploading)return;
        new AlertDialog.Builder(this).setTitle(tr("Language")).setItems(StudioStrings.NAMES,(dialog,index)->{getSharedPreferences("interface",0).edit().putString("language",StudioStrings.CODES[index]).apply();show();}).show();
    }
    private void login() {
        frame("LazyEdit Studio",false);button("Language",this::chooseLanguage);text("Your stories. Your private workspace.");
        EditText name=field("Username","",false);name.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD);
        EditText password=field("Password","",false);password.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);
        Spinner mode=choice("Workspace",new String[]{"Existing Pi","Private workspace"},"Existing Pi");
        mode.setVisibility(View.GONE);
        name.addTextChangedListener(new android.text.TextWatcher(){
            public void beforeTextChanged(CharSequence s,int start,int count,int after){}
            public void onTextChanged(CharSequence s,int start,int before,int count){mode.setVisibility(s.toString().trim().equals("lachlanchen")?View.VISIBLE:View.GONE);}
            public void afterTextChanged(android.text.Editable e){}
        });
        CheckBox register=check("Create account with invitation",false);EditText invitation=field("Invitation code (registration only)","",false);
        button("Sign in / Create account",()->task("Signing in and opening your workspace…",()->{
            String username=name.getText().toString().trim();
            api.login(username,password.getText().toString(),!username.equals("lachlanchen")||mode.getSelectedItemPosition()==1,register.isChecked()?invitation.getText().toString().trim():null);return true;
        },value->{password.setText("");screen=0;show();}));
        text("Sign in to your private workspace, or register with an invitation.");
        task("",()->api.json("/accounts/oauth/providers"),value->{JSONArray providers=value.optJSONArray("providers");if(providers!=null)for(int i=0;i<providers.length();i++){String provider=providers.getString(i);button(provider.equals("apple")?"Continue with Apple":"Continue with Google",()->oauthStart(provider,null));}});
    }
    private void oauthStart(String provider,String password) {
        task("Opening secure sign-in…",()->{
            byte[] bytes=new byte[32];new java.security.SecureRandom().nextBytes(bytes);
            String verifier=android.util.Base64.encodeToString(bytes,android.util.Base64.URL_SAFE|android.util.Base64.NO_WRAP|android.util.Base64.NO_PADDING);
            String challenge=android.util.Base64.encodeToString(java.security.MessageDigest.getInstance("SHA-256").digest(verifier.getBytes(java.nio.charset.StandardCharsets.UTF_8)),android.util.Base64.URL_SAFE|android.util.Base64.NO_WRAP|android.util.Base64.NO_PADDING);
            JSONObject body=new JSONObject().put("provider",provider).put("challenge",challenge).put("target","native");
            if(password!=null)body.put("link",true).put("password",password);
            String address=api.post("/accounts/oauth/start",body).getString("url");Uri uri=Uri.parse(address);
            if(!uri.getScheme().equals("https")||!Arrays.asList("appleid.apple.com","accounts.google.com").contains(uri.getHost()))throw new IOException("Invalid sign-in provider link.");
            oauthVerifier=verifier;return address;
        },address->startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(address))));
    }
    private void oauthReturn(Intent intent) {
        Uri uri=intent.getData();
        if(uri==null||!"art.lazying.lazyedit".equals(uri.getScheme())||!"auth".equals(uri.getHost())||oauthVerifier==null)return;
        String verifier=oauthVerifier,ticket=uri.getQueryParameter("ticket");oauthVerifier=null;
        if(ticket==null||!ticket.matches("[A-Za-z0-9_-]{43}")){message.setText("Sign-in was incomplete.");return;}
        task("Signing in and opening your workspace…",()->{api.oauthRedeem(ticket,verifier);return true;},ok->{screen=0;show();});
    }
    private void library(boolean hidden) {
        frame(hidden?"Removed videos":"Your Studio",true);
        button("Refresh",()->library(hidden));button(hidden?"Back to library":"Removed videos",()->library(!hidden));
        task("Opening your library…",()->{api.json("/auth/me");return api.json("/api/videos"+(hidden?"?hidden=true":""));},value->{
            libraryPage(value.optJSONArray("videos"),hidden,0);
        });
    }
    private void libraryPage(JSONArray videos,boolean hidden,int offset) throws Exception {
        // Bound native view creation for the owner's hundreds of recordings.
        frame(hidden?"Removed videos":"Your Studio",true);
        button("Refresh",()->library(hidden));button(hidden?"Back to library":"Removed videos",()->library(!hidden));
        if(videos==null||videos.length()==0){text("No videos yet. Add one in Upload.");return;}
        int end=Math.min(offset+20,videos.length());text((offset+1)+"–"+end+" of "+videos.length()+" videos");
        for(int i=offset;i<end;i++){
                JSONObject video=videos.getJSONObject(i);String title=video.optString("title","Video "+video.optInt("id"));
                text(title);text(video.optString("created_at"));
                button(hidden?"Restore":"Open video",()->{if(hidden)visibility(video,false);else video(video);});
                if(!hidden)button("Remove from library",()->new AlertDialog.Builder(this).setTitle("Remove this video?").setMessage("This hides the row. Media, runs and social posts are retained.").setPositiveButton("Remove",(d,w)->visibility(video,true)).setNegativeButton("Cancel",null).show());
        }
        if(offset>0)button("Previous page",()->{try{libraryPage(videos,hidden,Math.max(0,offset-20));}catch(Exception e){error(e);}});
        if(end<videos.length())button("Next page",()->{try{libraryPage(videos,hidden,end);}catch(Exception e){error(e);}});
    }
    private void visibility(JSONObject video,boolean hidden) {
        task("Updating library…",()->api.post("/v1/studio/videos/"+video.optInt("id")+"/visibility",new JSONObject().put("hidden",hidden)),value->library(!hidden));
    }
    private void video(JSONObject video) {
        int id=video.optInt("id");frame(video.optString("title","Video"),true);
        String media=video.optString("preview_media_url",video.optString("media_url"));
        if(!media.isEmpty())button("Preview video",()->{
            try { player=new VideoView(this);content.addView(player,0,new LinearLayout.LayoutParams(-1,dp(270)));MediaController controls=new MediaController(this);controls.setAnchorView(player);player.setMediaController(controls);player.setVideoURI(Uri.parse(StudioApi.url(media).toString()),Collections.singletonMap("Cookie",api.cookie()));player.start(); }
            catch(Exception e){error(e);}
        });
        button(api.publishingEnabled()?"Prepare & publish":"Edit & preview",()->composer(id));button("Full editor · subtitles, metadata & cover",()->openEditor("/editor?videoId="+id));
        button("Preview edited video",()->task("Reading status…",()->api.json("/api/videos/"+id+"/burn-subtitles"),render->{String output=render.optString("output_url");if(!render.optString("status").equals("completed")||output.isEmpty()){message.setText("Processing");return;}player=new VideoView(this);content.addView(player,0,new LinearLayout.LayoutParams(-1,dp(270)));MediaController controls=new MediaController(this);controls.setAnchorView(player);player.setMediaController(controls);player.setVideoURI(Uri.parse(StudioApi.url(output).toString()),Collections.singletonMap("Cookie",api.cookie()));player.start();}));
        button("Processing status",()->task("Reading status…",()->api.json("/api/videos/"+id+"/process-status"),value->message.setText(value.optJSONObject("steps")==null?value.toString():value.getJSONObject("steps").toString(2))));
    }
    private void activity() {
        frame(api.publishingEnabled()?"Publication activity":"Activity",true);button("Refresh",this::activity);
        task("Reading your queue…",()->api.json("/api/autopublish/queue"),value->{
            message.setText("");notifyAttention(value);JSONArray jobs=value.optJSONArray("jobs");if(jobs==null||jobs.length()==0)text("No publication tasks to show.");
            if(jobs!=null)for(int i=0;i<jobs.length();i++){
                JSONObject job=jobs.getJSONObject(i);text(job.optString("title",job.optString("filename","Publication")));text(job.optString("status")+" · "+job.optString("platforms"));
                if(!job.optString("error").isEmpty())text(job.optString("error"));
                JSONObject attention=job.optJSONObject("attention");if(attention!=null&&attention.optString("status").equals("required")){text(attention.optString("message","Login or verification required"));button("Open login / verification",()->openEditor(attention.optString("artifact_url","/home")));}
            }
            if(foreground)ui.postDelayed(poll,15000);
        });
    }
    private void account() {
        frame("Account",true);button("Language",this::chooseLanguage);text(api.username());text(api.mode().equals("owner")?"Existing Pi workspace":"Private Docker workspace");
        if(api.publishingEnabled())button("Enable login notifications",()->{if(Build.VERSION.SDK_INT>=33)requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"},73);else message.setText(tr("Login notifications"));});
        button("Full Studio",()->openEditor("/home"));
        button("Sign out",()->task("Signing out…",()->{api.logout();return true;},value->show()));
        task("Reading account…",()->api.json("/accounts/account").put("capabilities",api.json("/auth/me").optJSONObject("capabilities")).put("providers",api.json("/accounts/oauth/providers").optJSONArray("providers")).put("linked",api.json("/accounts/oauth/links").optJSONArray("providers")).put("billing",api.json("/accounts/billing/catalog")),value->{
            if(api.mode().equals("workspace")&&api.publishingEnabled())button("Platform accounts",()->openEditor("/platforms"));
            JSONObject catalog=value.optJSONObject("billing");if(catalog!=null&&catalog.optBoolean("enabled")&&catalog.optJSONArray("providers").toString().contains("google"))button("Plans and billing",this::billingScreen);
            JSONArray providers=value.optJSONArray("providers"),linked=value.optJSONArray("linked");
            if(providers!=null)for(int i=0;i<providers.length();i++){
                String provider=providers.getString(i);boolean found=false;
                if(linked!=null)for(int j=0;j<linked.length();j++)if(provider.equals(linked.getString(j)))found=true;
                final boolean unlink=found;
                String label=unlink?(provider.equals("apple")?"Unlink Apple account":"Unlink Google account"):(provider.equals("apple")?"Link Apple account":"Link Google account");
                button(label,()->{
                    EditText password=new EditText(this);password.setInputType(129);password.setHint(tr("Password"));
                    new AlertDialog.Builder(this).setTitle(tr(label)).setMessage(tr("Confirm your Studio password, then choose the provider account to link.")).setView(password)
                        .setNegativeButton(tr("Cancel"),(dialog,which)->password.setText(""))
                        .setPositiveButton(tr("Continue"),(dialog,which)->{
                            String proof=password.getText().toString();password.setText("");
                            if(unlink)task("Reading account…",()->api.post("/accounts/oauth/unlink",new JSONObject().put("provider",provider).put("password",proof)),ok->account());
                            else oauthStart(provider,proof);
                        }).show();
                });
            }
            message.setText("");if(!value.optString("role").equals("admin")){
                button("Delete account",()->{
                    EditText password=new EditText(this);password.setHint(tr("Password"));password.setInputType(129);
                    new AlertDialog.Builder(this).setTitle(tr("Delete account")).setMessage(tr("This permanently removes your private workspace and platform logins. Published posts remain on their platforms. Wait for active work to finish first.")).setView(password).setNegativeButton(tr("Cancel"),(dialog,which)->password.setText(""))
                        .setPositiveButton(tr("Delete account"),(dialog,which)->{
                            String proof=password.getText().toString();password.setText("");
                            task("Deleting account…",()->{api.post("/accounts/delete",new JSONObject().put("confirm",api.username()).put("password",proof));api.file("library.json").delete();api.file("upload.json").delete();api.clear();return true;},ok->show());
                        }).show();
                });return;
            }
            text("Administrator");
            button(api.mode().equals("owner")?"Switch to private Docker workspace":"Switch to existing Pi workspace",()->{
                if(api.file("upload.json").exists()||uploading){message.setText("Finish or remove your current upload before switching.");return;}
                task("Opening your workspace…",()->{api.switchMode();return true;},ok->{screen=3;show();});
            });
            button("Create invitation",()->task("Creating invitation…",()->api.post("/accounts/invite",new JSONObject()),invite->{
                String link=invite.getString("url");text("Single use · expires in 72 hours");
                button("Share invitation",()->{Intent share=new Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_TEXT,link);startActivity(Intent.createChooser(share,"Invite to Studio"));});
                button("Copy invitation",()->{((android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText("Studio invitation",link));message.setText("Invitation copied.");});
            }));
        });
    }
    private void billingScreen() {
        frame("Plans and billing",true);button("Back",()->{screen=3;show();});
        task("Reading account…",()->api.json("/accounts/billing/catalog"),catalog->{
            JSONArray providers=catalog.optJSONArray("providers");boolean google=false;
            if(providers!=null)for(int i=0;i<providers.length();i++)if(providers.getString(i).equals("google"))google=true;
            if(!catalog.optBoolean("enabled")||!google){text("Billing is being prepared. No charge will be made.");return;}
            text("Plans renew monthly. Cancel anytime in your store account.");
            billing=new StudioBilling(this,api,catalog,new StudioBilling.Display(){public void product(String label,Runnable buy){button(label,buy);}public void message(String text){message.setText(tr(text));}});
            button("Restore purchases",()->{if(billing!=null)billing.restore();});
            button("Manage subscription",()->startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse("https://play.google.com/store/account/subscriptions?package=art.lazying.lazyedit"))));
        });
    }
    private void uploadScreen() {
        frame("Upload video",true);text("Choose a video in Files. Uploads resume from the saved server position. Keep Studio open for the fastest transfer.");
        button("Choose video",()->{if(api.file("upload.json").exists()){message.setText("Finish or remove the current upload first.");return;}Intent pick=new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("video/*").addCategory(Intent.CATEGORY_OPENABLE).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);startActivityForResult(pick,42);});
        if(api.file("upload.json").exists()){
            try { text(new JSONObject(StudioApi.readFile(api.file("upload.json"))).optString("filename")); }catch(Exception e){error(e);}
            button("Upload / Resume",this::upload);Button pause=button("Pause",()->uploading=false);pause.setTag("pause-upload");pause.setOnClickListener(v->uploading=false);
            button("Remove unfinished upload",()->{if(uploading)return;api.file("upload.json").delete();uploadScreen();});
        }
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request!=42||result!=RESULT_OK||data==null||data.getData()==null)return;
        try {
            Uri uri=data.getData();getContentResolver().takePersistableUriPermission(uri,data.getFlags()&Intent.FLAG_GRANT_READ_URI_PERMISSION);
            String name="video.mp4";long size=-1;
            try(Cursor cursor=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE},null,null,null)) { if(cursor!=null&&cursor.moveToFirst()){name=cursor.getString(0);size=cursor.getLong(1);} }
            if(size<=0||size>10L*1024*1024*1024)throw new IOException("Choose a video between 1 byte and 10 GB.");
            StudioApi.writeFile(api.file("upload.json"),new JSONObject().put("uri",uri.toString()).put("filename",name).put("size",size).toString());screen=1;show();
        }catch(Exception e){error(e);}
    }
    private void upload() {
        if(uploading)return;uploading=true;File state=api.file("upload.json");
        task("Connecting upload…",()->{
            try {
                JSONObject pending=new JSONObject(StudioApi.readFile(state));long size=pending.getLong("size");
                if(!pending.has("uploadId")){JSONObject receipt=api.post("/v1/studio/uploads",new JSONObject().put("filename",pending.getString("filename")).put("title",pending.getString("filename")).put("size",size));pending.put("uploadId",receipt.getString("uploadId"));StudioApi.writeFile(state,pending.toString());}
                String id=pending.getString("uploadId");JSONObject position;
                try { position=api.json("/v1/studio/upload?uploadId="+id); }
                catch(StudioApi.Failure failure){if(failure.status==404){pending.remove("uploadId");StudioApi.writeFile(state,pending.toString());}throw failure;}
                JSONObject receipt=position.optJSONObject("receipt");if(receipt!=null){state.delete();return receipt;}
                long offset=position.getLong("offset");if(offset<0||offset>size)throw new IOException("Invalid upload position.");
                try(InputStream input=getContentResolver().openInputStream(Uri.parse(pending.getString("uri")))){
                    if(input==null)throw new IOException("Choose the video again; the file is unavailable.");
                    long skipped=0;while(skipped<offset){long n=input.skip(offset-skipped);if(n<=0){if(input.read()==-1)throw new EOFException();n=1;}skipped+=n;}
                    while(offset<size&&uploading){
                        byte[] bytes=new byte[(int)Math.min(8*1024*1024,size-offset)];int length=0;while(length<bytes.length){int n=input.read(bytes,length,bytes.length-length);if(n<0)throw new EOFException();length+=n;}
                        long next=api.chunk(id,offset,bytes);if(next!=offset+length)throw new IOException("Upload position changed. Resume to check it.");offset=next;
                        final long current=offset;ui.post(()->message.setText("Uploaded "+(current*100/size)+"%"));
                    }
                }
                if(!uploading)throw new IOException("Upload paused. Tap Resume when ready.");
                receipt=api.post("/v1/studio/upload-complete",new JSONObject().put("uploadId",id));state.delete();return receipt;
            }finally{uploading=false;}
        },receipt->{message.setText("Added to your Studio.");screen=0;show();});
    }
    private void composer(int id) {
        frame(api.publishingEnabled()?"Prepare & publish":"Edit & preview",true);String path="/v1/studio/videos/"+id;
        File pending=api.file("submission-"+id+".json");
        if(pending.exists()){
            text("A saved request needs confirmation. No second request has been sent.");
            button("Check saved request",()->task("Checking receipt…",()->{
                JSONObject intent=new JSONObject(StudioApi.readFile(pending));JSONObject status=api.json(path+"/submission?key="+intent.getString("key"));status.put("intent",intent);return status;
            },status->{
                if(status.optJSONObject("result")!=null){pending.delete();message.setText("Request confirmed. Follow Activity.");}
                else if(status.optString("state").equals("not_submitted")){JSONObject intent=status.getJSONObject("intent");new AlertDialog.Builder(this).setTitle("Retry the same saved request?").setMessage("Studio has no receipt. This reuses the original request ID.").setPositiveButton("Retry",(d,w)->submitSaved(path,pending,intent)).setNegativeButton("Cancel",null).show();}
                else message.setText("Studio received the request. Check Activity before doing anything else.");
            }));return;
        }
        task("Loading current settings…",()->api.json(path+"/composer"),result->{
            message.setText("");final boolean canPublish=result.optJSONObject("capabilities")!=null&&result.getJSONObject("capabilities").optBoolean("publishing");JSONObject form=result.getJSONObject("defaults");File draft=api.file("choices-"+id+".json");
            if(draft.exists())try{form=new JSONObject(StudioApi.readFile(draft));}catch(Exception ignored){}
            final JSONObject choices=form;
            boolean portrait=result.optJSONObject("geometry")!=null&&result.getJSONObject("geometry").optBoolean("portrait");
            CheckBox subtitles=check("Burn subtitles",form.optBoolean("burnSubtitles",true));
            EditText languages=field("Languages, bottom to top",join(form.optJSONArray("languages")),false);text("Examples: zh-Hant,ja,en · Japanese readings and Chinese pinyin use the normal renderer.");
            CheckBox correct=check("Correct subtitles with context",form.optBoolean("correct",true));
            EditText context=field("Background / script reference",form.optString("context"),true);
            CheckBox metadata=check("Use context for metadata",form.optBoolean("contextForMetadata",true));
            EditText direction=field("Metadata direction (optional)",form.optString("metadataDirection"),true);
            CheckBox logo=check("Burn configured Studio logo",form.optBoolean("logo",true));
            Spinner logoPosition=choice("Logo position",new String[]{"top-right","top-left","bottom-right","bottom-left"},form.optString("logoPosition"));
            Spinner background=choice("Background layout",portrait?new String[]{"off"}:new String[]{"off","bottom","center"},form.optString("background"));if(portrait)text("Portrait sources keep their original frame.");
            EditText bottom=field("Bottom space ratio",form.optString("bottomSpace","0.4"),false),lift=field("Subtitle lift",form.optString("lift","0"),false),rows=field("Reserved rows",form.optString("rows","4"),false),font=field("Font scale",form.optString("fontScale","1"),false);
            CheckBox bold=check("Bold text",form.optBoolean("fontBold",true)),outline=check("Bold outline",form.optBoolean("outlineBold",true));
            Spinner category=choice("Category",new String[]{"","simplelife","lalachan","musia","lalamv","lazyingart"},form.optString("category"));
            Map<String,CheckBox> platforms=new LinkedHashMap<>();List<String> selected=Arrays.asList(join(form.optJSONArray("platforms")).split(","));
            if(canPublish)for(String channel:new String[]{"shipinhao","instagram","youtube","douyin","xiaohongshu","bilibili"})platforms.put(channel,check(channel,selected.contains(channel)));
            JSONArray sessions=result.optJSONArray("sessions");List<String> runLabels=new ArrayList<>();List<Integer> runIds=new ArrayList<>();runLabels.add("New run");runIds.add(0);
            if(sessions!=null)for(int i=0;i<sessions.length();i++){JSONObject run=sessions.getJSONObject(i);runLabels.add("Reuse run #"+run.optInt("id"));runIds.add(run.optInt("id"));}
            Spinner run=choice("Publication run",runLabels.toArray(new String[0]),"New run");if(form.optString("mode").equals("reuse")){int selectedRun=runIds.indexOf(form.optInt("sessionID"));if(selectedRun>=0)run.setSelection(selectedRun);}
            Runnable review=()->{
                try {
                    choices.put("burnSubtitles",subtitles.isChecked()).put("languages",array(languages.getText().toString())).put("correct",correct.isChecked()).put("context",context.getText().toString()).put("metadataDirection",direction.getText().toString()).put("contextForMetadata",metadata.isChecked());
                    choices.put("logo",logo.isChecked()).put("logoPosition",logoPosition.getSelectedItem().toString()).put("background",background.getSelectedItem().toString()).put("bottomSpace",Double.parseDouble(bottom.getText().toString())).put("lift",Double.parseDouble(lift.getText().toString())).put("rows",Integer.parseInt(rows.getText().toString())).put("fontScale",Double.parseDouble(font.getText().toString())).put("fontBold",bold.isChecked()).put("outlineBold",outline.isChecked()).put("category",category.getSelectedItem().toString());
                    JSONArray targets=new JSONArray();for(Map.Entry<String,CheckBox> channel:platforms.entrySet())if(channel.getValue().isChecked())targets.put(channel.getKey());choices.put("platforms",targets).put("mode",run.getSelectedItemPosition()==0?"new":"reuse").put("sessionID",runIds.get(run.getSelectedItemPosition()));
                    StudioApi.writeFile(draft,choices.toString());
                    task("Reviewing your choices…",()->api.post(path+"/plan",choices),plan->{AlertDialog.Builder reviewDialog=new AlertDialog.Builder(this).setTitle(tr("Review choices")).setMessage(joinLines(plan.optJSONArray("summary"))).setNegativeButton(tr("Cancel"),null);if(!choices.optString("mode").equals("reuse"))reviewDialog.setNeutralButton(tr("Prepare only"),(d,w)->confirm(path,pending,choices,plan,"prepare"));if(canPublish)reviewDialog.setPositiveButton(tr("Publish"),(d,w)->confirm(path,pending,choices,plan,"publish"));reviewDialog.show();});
                }catch(Exception e){error(e);}
            };
            button("Review choices",review);button("Full editor",()->openEditor("/editor?videoId="+id));
        });
    }
    private void confirm(String path,File file,JSONObject form,JSONObject plan,String action) {
        new AlertDialog.Builder(this).setTitle(action.equals("publish")?"Publish to selected platforms?":"Prepare this video?").setMessage(action.equals("publish")?"This sends a real publication task to your workspace queue.":"No social post will be made.").setPositiveButton("Confirm",(d,w)->{
            if(busy||file.exists()){message.setText("Follow the saved request before submitting again.");return;}
            try{JSONObject body=new JSONObject().put("action",action).put("confirmation",action.equals("publish")?"PUBLISH":"").put("form",form).put("planDigest",plan.getString("planDigest"));JSONObject intent=new JSONObject().put("key",UUID.randomUUID().toString()).put("body",body);StudioApi.writeFile(file,intent.toString());submitSaved(path,file,intent);}catch(Exception e){error(e);}
        }).setNegativeButton("Cancel",null).show();
    }
    private void submitSaved(String path,File file,JSONObject intent) {
        task("Sending the saved request…",()->{
            try{JSONObject result=api.post(path+"/submit",intent.getJSONObject("body"),intent.getString("key"));file.delete();return result;}
            catch(StudioApi.Failure failure){if(failure.rejected)file.delete();throw failure;}
        },value->{screen=2;show();});
    }
    private JSONArray array(String value) { JSONArray result=new JSONArray();for(String item:value.split(","))if(!item.trim().isEmpty())result.put(item.trim());return result; }
    private String join(JSONArray value) { if(value==null)return "";List<String> rows=new ArrayList<>();for(int i=0;i<value.length();i++)rows.add(value.optString(i));return String.join(",",rows); }
    private String joinLines(JSONArray value) { return join(value).replace(",","\n"); }
    private void openEditor(String path) {
        try{StudioApi.url(path);}catch(Exception e){error(e);return;}
        frame("Studio editor",false);button("Done",()->{CookieManager.getInstance().removeAllCookies(null);show();});
        editor=new WebView(this);content.addView(editor,new LinearLayout.LayoutParams(-1,dp(620)));
        editor.getSettings().setJavaScriptEnabled(true);editor.getSettings().setDomStorageEnabled(true);editor.getSettings().setAllowFileAccess(false);editor.getSettings().setAllowContentAccess(false);editor.getSettings().setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        editor.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView web,WebResourceRequest request){try{StudioApi.url(request.getUrl().toString());return false;}catch(Exception e){return true;}}});
        CookieManager manager=CookieManager.getInstance();manager.removeAllCookies(removed->{for(String cookie:api.cookie().split("; "))if(!cookie.isEmpty())manager.setCookie(StudioApi.ORIGIN,cookie+"; Path=/; Secure; HttpOnly; SameSite=Strict");try{editor.loadUrl(Uri.parse(StudioApi.url(path).toString()).buildUpon().appendQueryParameter("interfaceLanguage",StudioStrings.language(this)).build().toString());}catch(Exception e){error(e);}});
    }
    @Override public void onBackPressed(){if(busy){message.setText("Please wait for the current request.");return;}if(editor!=null){CookieManager.getInstance().removeAllCookies(null);show();}else if(screen!=0){screen=0;show();}else super.onBackPressed();}
    private void checkAttention() {
        final String scope=api.scope();
        worker.execute(()->{try { JSONObject queue=api.json("/api/autopublish/queue");ui.post(()->{if(foreground&&api.signedIn()&&scope.equals(api.scope()))notifyAttention(queue);}); }catch(Exception ignored){} });
    }
    private void notifyAttention(JSONObject queue) {
        if(Build.VERSION.SDK_INT>=33&&checkSelfPermission("android.permission.POST_NOTIFICATIONS")!=android.content.pm.PackageManager.PERMISSION_GRANTED)return;
        android.app.NotificationManager manager=(android.app.NotificationManager)getSystemService(NOTIFICATION_SERVICE);
        if(!manager.areNotificationsEnabled())return;
        if(Build.VERSION.SDK_INT>=26)manager.createNotificationChannel(new android.app.NotificationChannel("login",tr("Login notifications"),android.app.NotificationManager.IMPORTANCE_DEFAULT));
        JSONArray jobs=queue.optJSONArray("jobs");if(jobs==null)return;
        android.content.SharedPreferences seen=getSharedPreferences("notifications-"+api.scope(),0);
        if(seen.getAll().size()>256)seen.edit().clear().apply();
        for(int i=0;i<jobs.length();i++) {
            JSONObject job=jobs.optJSONObject(i);if(job==null)continue;JSONObject attention=job.optJSONObject("attention");
            if(attention==null||!attention.optString("status").equals("required"))continue;
            String key=job.optString("id")+":"+job.optString("status");if(seen.getBoolean(key,false))continue;
            Intent open=new Intent(this,MainActivity.class).putExtra("attentionScope",api.scope());
            android.app.PendingIntent pending=android.app.PendingIntent.getActivity(this,key.hashCode(),open,android.app.PendingIntent.FLAG_UPDATE_CURRENT|android.app.PendingIntent.FLAG_IMMUTABLE);
            manager.notify(key.hashCode(),new androidx.core.app.NotificationCompat.Builder(this,"login").setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle("LazyEdit Studio").setContentText(tr("Login or verification required")).setVisibility(androidx.core.app.NotificationCompat.VISIBILITY_PRIVATE).setContentIntent(pending).setAutoCancel(true).build());
            seen.edit().putBoolean(key,true).apply();
        }
    }
    @Override protected void onNewIntent(Intent intent){super.onNewIntent(intent);setIntent(intent);oauthReturn(intent);if(api.signedIn()&&api.scope().equals(intent.getStringExtra("attentionScope"))){screen=2;show();}}
    @Override protected void onStart(){super.onStart();foreground=true;if(screen==2&&api!=null&&api.signedIn())ui.postDelayed(poll,1000);ui.postDelayed(attentionPoll,30000);}
    @Override protected void onStop(){super.onStop();foreground=false;ui.removeCallbacks(poll);ui.removeCallbacks(attentionPoll);uploading=false;if(player!=null)player.pause();}
    @Override protected void onDestroy(){if(billing!=null)billing.close();ui.removeCallbacks(poll);ui.removeCallbacks(attentionPoll);uploading=false;if(editor!=null)editor.destroy();worker.shutdownNow();super.onDestroy();}
}
