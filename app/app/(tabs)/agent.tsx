import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Linking, Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';
import { useIsFocused } from '@react-navigation/native';
import * as DocumentPicker from 'expo-document-picker';
import { useI18n } from '@/components/I18nProvider';
import { useStudioCapabilities } from '@/lib/studioCapabilities';
import { studioStorage } from '@/lib/studioStorage';
import { uploadRemoteVideo } from '@/lib/remoteStudioUpload';

const base = process.env.EXPO_PUBLIC_API_URL || '';
const remote = process.env.EXPO_PUBLIC_REMOTE_STUDIO === '1';
const root = '/v1/studio/agent/chats';
const uuid = () => globalThis.crypto.randomUUID();
type Turn = {id:string;text:string;reply:string;state:string;error?:string;summary?:string[];receipt?:{job_id?:number}};
type Chat = {id:string;videoId:number;title:string;messages:Turn[];job?:any;process?:any;preparation?:any;preview?:string};
type Saved = {chatId:string;id:string;message:string;action:string;language:string};
async function api(path:string, data?:unknown, key?:string) {
  const res=await fetch(base+path,{method:data?'POST':'GET',headers:data?{'Content-Type':'application/json',...(key?{'Idempotency-Key':key}:{})}:undefined,body:data?JSON.stringify(data):undefined});
  const value=await res.json();if(!res.ok)throw Object.assign(Error(typeof value.error==='string'?value.error:'Studio request failed'),{rejected:value.submissionState==='rejected'});return value;
}

export default function AgentScreen() {
  const {t,locale}=useI18n(),{publishing}=useStudioCapabilities(),focused=useIsFocused();
  const [chats,setChats]=useState<any[]>([]),[videos,setVideos]=useState<any[]>([]),[chat,setChat]=useState<Chat|null>(null);
  const [message,setMessage]=useState(''),[publish,setPublish]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
  const [pending,setPending]=useState<Saved|null>(null),[choose,setChoose]=useState(false),[uploadProgress,setUploadProgress]=useState<number|null>(null);
  const refreshList=useCallback(async()=>{const list=await api(root);setChats(list.chats);},[]);
  const accept=useCallback((value:Chat)=>{
    setChat(value);studioStorage.setItem('agent-chat',value.id);
    const raw=studioStorage.getItem('agent-pending');
    if(raw){const saved=JSON.parse(raw) as Saved;const turn=value.id===saved.chatId&&value.messages.find(m=>m.id===saved.id);
      if(turn&&['submitted','reply','rejected','held'].includes(turn.state)){studioStorage.removeItem('agent-pending');setPending(null);}}
  },[]);
  const open=useCallback(async(id:string)=>accept(await api(root+'/'+id)),[accept]);
  useEffect(()=>{if(!remote||!focused)return;let live=true;
    (async()=>{try{const raw=studioStorage.getItem('agent-pending');if(raw)setPending(JSON.parse(raw));await refreshList();const saved=studioStorage.getItem('agent-chat');if(saved&&live)await open(saved);}catch(e:any){if(live)setError(e.message);}})();
    return()=>{live=false;};
  },[focused,refreshList,open]);
  useEffect(()=>{if(!remote||!focused||!chat)return;let live=true;
    const timer=setInterval(async()=>{if(document.hidden)return;try{const next=await api(root+'/'+chat.id);if(live)accept(next);}catch(e:any){if(live)setError(e.message);}},10000);
    return()=>{live=false;clearInterval(timer);};
  },[focused,chat?.id,accept]);
  async function work(fn:()=>Promise<void>){if(busy)return;setBusy(true);setError('');try{await fn();}catch(e:any){setError(e.message);}finally{setBusy(false);setUploadProgress(null);}}
  async function attach(id:number){const value=await api(root,{id:uuid(),videoId:id});accept(value);setChoose(false);await refreshList();}
  async function upload(){const result=await DocumentPicker.getDocumentAsync({type:'video/*',multiple:false,copyToCacheDirectory:false});if(result.canceled)return;
    await work(async()=>{const asset=result.assets[0],blob=asset.file||await(await fetch(asset.uri)).blob();setUploadProgress(0);
      const done=await uploadRemoteVideo(base,blob,asset.name,setUploadProgress);await attach(done.json.videoId);});}
  async function send(saved?:Saved){if(!chat)return;await work(async()=>{
    const request=saved||{chatId:chat.id,id:uuid(),message:message.trim(),action:publish&&publishing?'publish':'prepare',language:locale};
    // Persist before transmission. Retry always uses these exact bytes and ID.
    studioStorage.setItem('agent-pending',JSON.stringify(request));setPending(request);setMessage('');
    const {chatId,...body}=request;
    try{accept(await api(root+'/'+chatId+'/messages',body,'agent-'+request.id));}
    catch(e:any){if(e.rejected){studioStorage.removeItem('agent-pending');setPending(null);setMessage(request.message);}throw e;}
  });}
  const button=(label:string,action:()=>void,disabled=false)=><Pressable accessibilityRole="button" disabled={disabled||busy} onPress={action} style={[styles.button,(disabled||busy)&&{opacity:0.45}]}><Text style={styles.buttonText}>{t(label)}</Text></Pressable>;
  if(!remote)return <View style={styles.page}><Text style={styles.title}>{t('Agent')}</Text><Text>{t('Open your secure Studio to chat with your videos.')}</Text>{button('Open Studio',()=>Linking.openURL('https://edit.lazying.art/agent'))}</View>;
  return <ScrollView style={styles.page} contentContainerStyle={styles.body} keyboardShouldPersistTaps="handled">
    <View style={styles.heading}><View style={{flex:1}}><Text style={styles.title}>{t('Agent')}</Text><Text style={styles.muted}>{t('Attach a video. Tell Studio what to do.')}</Text></View><Text style={styles.badge}>{t('Your Studio defaults')}</Text></View>
    <View style={styles.row}>{button('Attach video',()=>void upload(),!!pending)}{button('Choose from Studio',()=>void work(async()=>{setVideos((await api('/api/videos')).videos||[]);setChoose(!choose);}),!!pending)}</View>
    {choose&&<View style={styles.card}>{videos.slice(0,100).map(v=><Pressable key={v.id} onPress={()=>void work(()=>attach(v.id))} disabled={busy}><Text style={styles.link}>{v.title||v.filename||`Video ${v.id}`}</Text></Pressable>)}</View>}
    {chats.length>0&&<ScrollView horizontal showsHorizontalScrollIndicator={false}><View style={styles.row}>{chats.map(c=><Pressable key={c.id} disabled={busy} onPress={()=>void work(()=>open(c.id))} style={[styles.chip,c.id===chat?.id&&styles.selected]}><Text numberOfLines={1} style={{maxWidth:220}}>{c.title}</Text></Pressable>)}</View></ScrollView>}
    {error&&<Text accessibilityRole="alert" style={styles.error}>{error}</Text>}
    {uploadProgress!==null&&<Text>{t('Uploading video')} · {Math.round(uploadProgress*100)}%</Text>}
    {busy&&<ActivityIndicator accessibilityLabel={t('Working…')}/>}
    {chat?<>
      <Text style={styles.videoTitle}>{chat.title}</Text>
      {!chat.messages.length&&<View style={styles.card}><Text>{t('Describe the story, subtitle languages, layout and where to publish. Context guides corrections; it does not replace speech.')}</Text></View>}
      {chat.messages.map(m=><View key={m.id} style={{gap:10}}>
        <View style={styles.userBubble}><Text selectable>{m.text}</Text></View>
        <View style={styles.card}>
          <Text style={styles.state}>{t('agent_state_'+m.state)}</Text>
          {!!m.reply&&<Text selectable>{m.reply}</Text>}
          {m.summary?.map((line,i)=><Text key={i} style={styles.muted}>{line}</Text>)}
          {!!m.receipt?.job_id&&<Text>{t('Publication job')} #{m.receipt.job_id}</Text>}
          {!!m.error&&<Text style={styles.error}>{m.error}</Text>}
        </View>
      </View>)}
      {(chat.job||chat.process)&&<View style={styles.card}>
        <Text style={styles.videoTitle}>{t('Live progress')}</Text>
        {chat.job&&<><Text>{t('Publication job')} #{chat.job.id} · {String(chat.job.status)}</Text>{!!chat.job.error&&<Text style={styles.error}>{String(chat.job.error)}</Text>}{chat.job.attention?.status==='required'&&<Text style={styles.error}>{String(chat.job.attention.message||t('Login or verification required'))}</Text>}</>}
        {chat.preparation&&<Text>{t('Preparation')} · {String(chat.preparation.state)}</Text>}
        {Object.entries(chat.process?.steps||{}).map(([name,step]:[string,any])=><Text key={name} style={styles.muted}>{name} · {String(step.status||'')}{step.error?' · '+String(step.error):''}</Text>)}
        {chat.preview&&button('Preview edited video',()=>{const url=new URL(chat.preview!,location.origin);if(url.origin===location.origin)void Linking.openURL(url.href);})}
        {button('Open Activity',()=>void Linking.openURL('/library'))}
      </View>}
      {pending?<View style={styles.card}><Text>{t('A saved message is waiting for its receipt. Checking it will not create another task.')}</Text>{button('Check / retry saved message',()=>void send(pending))}</View>:<View style={styles.composer}>
        {publishing&&<View style={styles.row}><Switch value={publish} onValueChange={setPublish} disabled={busy} accessibilityLabel={t('Publish after editing')}/><Text>{t('Publish after editing')}</Text></View>}
        <Text style={styles.muted}>{t(publish&&publishing?'Send authorizes publication to the platforms in your instructions or saved defaults.':'Studio will prepare an edited preview. Nothing will be posted.')}</Text>
        <TextInput accessibilityLabel={t('Message Studio')} placeholder={t('Message Studio')} multiline value={message} onChangeText={setMessage} editable={!busy} maxLength={16000} style={styles.input}/>
        {button('Send',()=>void send(),!message.trim())}
      </View>}
    </>:<Text style={styles.muted}>{t('Attach or choose a video to begin.')}</Text>}
  </ScrollView>;
}
const styles=StyleSheet.create({page:{flex:1,backgroundColor:'#f4f7f6'},body:{padding:20,paddingBottom:110,gap:16,width:'100%',maxWidth:860,alignSelf:'center'},heading:{flexDirection:'row',gap:12,alignItems:'center'},title:{fontSize:30,fontWeight:'700',color:'#17392f'},videoTitle:{fontSize:17,fontWeight:'600',color:'#17392f'},muted:{color:'#596b65',fontSize:14,lineHeight:21},badge:{borderRadius:12,padding:10,backgroundColor:'#e4efe9',color:'#315a4b',fontSize:12},row:{flexDirection:'row',gap:10,alignItems:'center',flexWrap:'wrap'},button:{backgroundColor:'#235c48',borderRadius:12,paddingHorizontal:16,paddingVertical:12,alignSelf:'flex-start'},buttonText:{color:'white',fontWeight:'600'},card:{backgroundColor:'#fff',borderWidth:1,borderColor:'#e1e9e5',borderRadius:16,padding:18,gap:8},userBubble:{backgroundColor:'#deeee5',borderRadius:16,padding:18,marginLeft:32,gap:8},state:{fontWeight:'600',color:'#235c48'},chip:{padding:12,borderRadius:12,backgroundColor:'#eaf0ed'},selected:{backgroundColor:'#cfe5d8'},input:{minHeight:105,maxHeight:240,padding:14,backgroundColor:'white',borderRadius:12,borderWidth:1,borderColor:'#c3d5cb',fontSize:16,textAlignVertical:'top'},composer:{gap:12,paddingTop:8},error:{color:'#9c332b'},link:{color:'#235c48',paddingVertical:12}});
