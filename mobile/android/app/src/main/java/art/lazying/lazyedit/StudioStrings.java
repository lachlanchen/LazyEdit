package art.lazying.lazyedit;

import android.content.Context;
import org.json.JSONObject;
import java.util.Locale;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.util.HashMap;

/** Public interface dictionaries. Selection contains no account or media data. */
final class StudioStrings {
    static final String[] CODES={"en","zh-Hans","zh-Hant","ja","ko","vi","ar","fr","es","de","ru"};
    static final String[] NAMES={"English","简体中文","繁體中文","日本語","한국어","Tiếng Việt","العربية","Français","Español","Deutsch","Русский"};
    private static final HashMap<String,JSONObject> tables=new HashMap<>();
    static String language(Context context) {
        String saved=context.getSharedPreferences("interface",0).getString("language","");
        if(!saved.isEmpty())return saved;
        Locale locale=Locale.getDefault();String code=locale.getLanguage();
        if(code.equals("zh"))return locale.getScript().equals("Hant")||locale.getCountry().equals("TW")||locale.getCountry().equals("HK")?"zh-Hant":"zh-Hans";
        for(String value:CODES)if(value.equals(code))return code;
        return "en";
    }
    static String text(Context context,String value) {
        String code=language(context);JSONObject table=tables.get(code);
        if(table==null) {
            try(InputStream stream=context.getAssets().open("studio-locales/"+code+".json")) {
                ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[4096];int count;
                while((count=stream.read(buffer))!=-1)bytes.write(buffer,0,count);
                table=new JSONObject(bytes.toString("UTF-8"));
            }
            catch(Exception ignored) { table=new JSONObject(); }
            tables.put(code,table);
        }
        return table.optString(value,value);
    }
}
