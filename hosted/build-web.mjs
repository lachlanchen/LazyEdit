import { readFileSync, writeFileSync } from 'node:fs';
const path='/opt/lazyedit/webdist/index.html';
let html=readFileSync(path,'utf8');
html=html.replace('</head>','<script src="/studio-session.js" defer></script></head>');
html=html.replace('</body>',readFileSync('/opt/lazyedit/studio/web/loading.html','utf8')+'<a href="/platforms" style="position:fixed;right:12px;bottom:116px;z-index:9999;background:white;color:#264ee4;border:1px solid #dde3f0;border-radius:18px;padding:7px 12px;font:13px system-ui;text-decoration:none">Platform accounts</a></body>');
writeFileSync(path,html);
const login='/opt/lazyedit/studio/web/login.html';
writeFileSync(login,readFileSync(login,'utf8').replace(' value="lachlanchen"',''));
