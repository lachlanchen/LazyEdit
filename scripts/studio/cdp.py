#!/usr/bin/env python
"""Small visible-tab CDP client; attach one target without enumerating stuck tabs."""
import argparse,json,pathlib,requests,websocket,itertools
class Tab:
 def __init__(self,port,target=None,url=None):
  base=f'http://127.0.0.1:{port}'
  if url:self.info=requests.put(base+'/json/new',params=url,timeout=15).json()
  else:self.info=next(t for t in requests.get(base+'/json/list',timeout=15).json() if t['id']==target)
  self.ws=websocket.create_connection(self.info['webSocketDebuggerUrl'],timeout=30,suppress_origin=True);self.ids=itertools.count(1)
 def call(self,method,params=None):
  id=next(self.ids);self.ws.send(json.dumps({'id':id,'method':method,'params':params or {}}))
  while True:
   d=json.loads(self.ws.recv())
   if d.get('id')==id:
    if 'error' in d:raise RuntimeError(d['error'])
    return d.get('result',{})
 def evaluate(self,js):
  result=self.call('Runtime.evaluate',{'expression':js,'returnByValue':True,'awaitPromise':True})
  if 'exceptionDetails' in result:raise RuntimeError(result['exceptionDetails'].get('text','Page JavaScript failed'))
  return result.get('result',{}).get('value')
 def close(self):self.ws.close()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=9484);p.add_argument('--target');p.add_argument('--url');p.add_argument('--expression',default='document.body.innerText');a=p.parse_args();t=Tab(a.port,a.target,a.url);t.call('Page.bringToFront');print(json.dumps({'id':t.info['id'],'result':t.evaluate(a.expression)},ensure_ascii=False));t.close()
