package art.lazying.lazyedit;

import android.content.Context;
import android.content.Intent;
import android.content.ComponentName;
import android.os.SystemClock;
import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.json.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;
import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.*;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.assertion.ViewAssertions.doesNotExist;
import static androidx.test.espresso.matcher.ViewMatchers.*;
import static org.junit.Assert.*;
import java.io.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Dedicated disposable emulator only. Never submits a social publication. */
@RunWith(AndroidJUnit4.class)
public class StudioNativeTest {
    private void waitText(String text,long timeout) throws Exception {
        long end=System.currentTimeMillis()+timeout;
        while(System.currentTimeMillis()<end) {
            try { onView(withText(text)).check(matches(isDisplayed()));return; }
            catch(AssertionError|RuntimeException ignored) { SystemClock.sleep(250); }
        }
        onView(withText(text)).check(matches(isDisplayed()));
    }
    private void tap(String text) { onView(withText(text)).perform(scrollTo(),click()); }
    private void ready(ActivityScenario<MainActivity> scenario) {
        long deadline=System.currentTimeMillis()+120000;AtomicBoolean working=new AtomicBoolean(true);
        while(System.currentTimeMillis()<deadline){scenario.onActivity(a->working.set(a.isWorking()));if(!working.get())return;SystemClock.sleep(200);}
        fail("Native request did not finish");
    }
    @Test public void ownerNativeNavigationAndWorkspaceSwitch() throws Exception {
        Context context=InstrumentationRegistry.getInstrumentation().getTargetContext();
        File credential=new File(context.getFilesDir(),"qa-credentials.json");
        assertTrue("Prepare private QA credentials in the dedicated emulator",credential.isFile());
        JSONObject account=new JSONObject(StudioApi.readFile(credential));
        StudioApi previous=new StudioApi(context);
        if(previous.signedIn())previous.logout();
        Intent launch=new Intent().setComponent(new ComponentName("art.lazying.lazyedit",MainActivity.class.getName())).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        try(ActivityScenario<MainActivity> scenario=ActivityScenario.launch(launch)) {
            onView(withHint("Username")).perform(replaceText(account.getString("username")),closeSoftKeyboard());
            onView(withHint("Password")).perform(replaceText(account.getString("password")),closeSoftKeyboard());
            tap("Sign in / Create account");waitText("Your Studio",60000);ready(scenario);
            onView(withText("Upload")).perform(click());waitText("Upload video",10000);
            onView(withText("Activity")).perform(click());waitText("Publication activity",10000);
            ready(scenario);
            onView(withText("Account")).perform(click());waitText("Existing Pi workspace",10000);ready(scenario);
            long deadline=System.currentTimeMillis()+30000;
            while(System.currentTimeMillis()<deadline) { try { tap("Create invitation");break; }catch(RuntimeException ignored){SystemClock.sleep(300);} }
            ready(scenario);onView(withText("Share invitation")).perform(scrollTo()).check(matches(isDisplayed()));
            tap("Switch to private Docker workspace");waitText("Private Docker workspace",240000);
            ready(scenario);tap("Switch to existing Pi workspace");waitText("Existing Pi workspace",60000);ready(scenario);
            scenario.recreate();waitText("Your Studio",30000);
        } finally {
            credential.delete();StudioApi current=new StudioApi(context);
            if(current.signedIn())current.logout();
        }
    }
    @Test public void requestsStayInTheAuthenticatedOrigin() throws Exception {
        assertEquals("edit.lazying.art",StudioApi.url("/api/videos").getHost());
        for(String invalid:new String[]{"http://edit.lazying.art/","https://evil.test/","https://user@edit.lazying.art/","https://edit.lazying.art:444/"}) {
            try { StudioApi.url(invalid);fail("Untrusted destination accepted"); }catch(IOException expected) {}
        }
    }
    @Test public void memberEditingDoesNotRequireSocialAccounts() throws Exception {
        Context context=InstrumentationRegistry.getInstrumentation().getTargetContext();
        File credential=new File(context.getFilesDir(),"qa-member-credentials.json");
        assertTrue("Prepare private member credentials in the dedicated emulator",credential.isFile());
        JSONObject account=new JSONObject(StudioApi.readFile(credential));
        StudioApi previous=new StudioApi(context);if(previous.signedIn())previous.logout();
        Intent launch=new Intent().setComponent(new ComponentName("art.lazying.lazyedit",MainActivity.class.getName())).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        try(ActivityScenario<MainActivity> scenario=ActivityScenario.launch(launch)) {
            onView(withHint("Username")).perform(replaceText(account.getString("username")),closeSoftKeyboard());
            onView(withHint("Password")).perform(replaceText(account.getString("password")),closeSoftKeyboard());
            tap("Sign in / Create account");waitText("Your Studio",90000);ready(scenario);
            StudioApi memberApi=new StudioApi(context);
            JSONObject memberSession=memberApi.json("/auth/me");
            assertFalse(memberSession.getJSONObject("capabilities").getBoolean("publishing"));
            assertFalse(memberApi.publishingEnabled());
            onView(withText("Account")).perform(click());waitText("Private Docker workspace",30000);ready(scenario);
            onView(withText("Platform accounts")).check(doesNotExist());
            onView(withText("Create invitation")).check(doesNotExist());
            tap("Sign out");waitText("Sign in / Create account",15000);
        } finally {
            credential.delete();StudioApi current=new StudioApi(context);if(current.signedIn())current.logout();
        }
    }
}
