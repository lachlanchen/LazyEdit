// Public UI dictionaries only. Never store passwords, QR codes or media here.
const languages=[['en','English'],['zh-Hans','简体中文'],['zh-Hant','繁體中文'],['ja','日本語'],['ko','한국어'],['vi','Tiếng Việt'],['ar','العربية'],['fr','Français'],['es','Español'],['de','Deutsch'],['ru','Русский']];
const key='studio.interfaceLanguage', original=new WeakMap();let table={},generation=0;
const language=()=>{const fromURL=new URL(location.href).searchParams.get('interfaceLanguage');return fromURL||localStorage.getItem(key)||navigator.language;};
function normalize(value){if(languages.some(([c])=>c===value))return value;if(value?.startsWith('zh'))return /Hant|TW|HK/.test(value)?'zh-Hant':'zh-Hans';const prefix=value?.slice(0,2);return languages.some(([c])=>c===prefix)?prefix:'en';}
function translate(){
  const nodes=document.createTreeWalker(document.querySelector('main')||document.body,NodeFilter.SHOW_TEXT);
  while(nodes.nextNode()){
    const node=nodes.currentNode;if(node.parentElement?.closest('script,style,textarea,select[data-interface-language],input'))continue;
    const saved=original.get(node), current=node.textContent;
    const source=saved&&current===saved.rendered?saved.source:current;
    const clean=source.trim();const translated=table[clean];
    const rendered=translated?source.replace(clean,translated):source;
    if(current!==rendered)node.textContent=rendered;
    original.set(node,{source,rendered});
  }
  for(const node of document.querySelectorAll('[placeholder]')){const source=node.dataset.interfacePlaceholder||node.getAttribute('placeholder');node.dataset.interfacePlaceholder=source;node.setAttribute('placeholder',table[source]||source);}
}
async function change(code){const current=++generation;localStorage.setItem(key,code);document.documentElement.lang=code;document.documentElement.dir=code==='ar'?'rtl':'ltr';
  try{const response=await fetch((location.pathname.startsWith('/accounts')?'/accounts/locales/':'/studio-locales/')+code+'.json');if(!response.ok)return;const values=await response.json();if(current!==generation)return;table=values;translate();}catch{}
}
const picker=document.createElement('select');picker.dataset.interfaceLanguage='';picker.setAttribute('aria-label','Language');
for(const [code,name]of languages){const option=document.createElement('option');option.value=code;option.textContent=name;picker.append(option);}
picker.value=normalize(language());picker.onchange=()=>change(picker.value);
(document.querySelector('main')||document.body).prepend(picker);
new MutationObserver(()=>translate()).observe(document.querySelector('main')||document.body,{childList:true,subtree:true,characterData:true});
change(picker.value);
window.addEventListener('studio-language',()=>{picker.value=normalize(language());change(picker.value);});
