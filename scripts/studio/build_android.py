#!/usr/bin/env python
"""Build signed private beta APK/AAB, with owner-only signing outside Git."""
import os,pathlib,json,secrets,subprocess
os.umask(0o077)
r=pathlib.Path(__file__).resolve().parents[2];p=pathlib.Path.home()/'.config/lazyedit-studio/android';p.mkdir(parents=True,exist_ok=True)
meta=p/'signing.json'
if not meta.exists():meta.write_text(json.dumps({'password':secrets.token_urlsafe(30),'alias':'lazyedit-upload'},indent=2))
s=json.loads(meta.read_text());env=dict(os.environ,LAZYEDIT_KEYSTORE=str(p/'upload.jks'),LAZYEDIT_STORE_PASSWORD=s['password'],LAZYEDIT_KEY_PASSWORD=s['password'],LAZYEDIT_KEY_ALIAS=s['alias'],ANDROID_HOME=str(pathlib.Path.home()/'Android/Sdk'),JAVA_HOME=str(pathlib.Path.home()/'.sdkman/candidates/java/21.0.10-tem'))
if not (p/'upload.jks').exists():subprocess.run(['keytool','-genkeypair','-keystore',str(p/'upload.jks'),'-storepass:env','LAZYEDIT_STORE_PASSWORD','-keypass:env','LAZYEDIT_KEY_PASSWORD','-alias',s['alias'],'-keyalg','RSA','-keysize','3072','-validity','10000','-dname','CN=LazyEdit Studio, O=LazyingArt, C=HK'],env=env,check=True)
subprocess.run(['./gradlew','--no-daemon','--max-workers=2','-Dorg.gradle.jvmargs=-Xmx2048m','assembleRelease','bundleRelease'],cwd=r/'mobile/android',env=env,check=True)
