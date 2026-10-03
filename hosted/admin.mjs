#!/usr/bin/env node
// Run by the host operator, never from the public service. No Docker socket in gateway.
import { readFileSync, writeFileSync, mkdirSync, existsSync, chmodSync, statSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { Registry } from './store.mjs';
import { secret } from '../studio/auth.mjs';
import { workspaceCompose } from './compose.mjs';
process.umask(0o077);
const [command, directory, arg] = process.argv.slice(2);
if(!directory)throw Error('Usage: node hosted/admin.mjs init|invite|status|provision|retry STATE_DIR [domain|workspace-id]');
const root=resolve(directory), configPath=join(root,'config.json');
if(command==='init'){
  if(existsSync(configPath))throw Error('Already initialized');
  if(!arg||!/^[a-z0-9.-]+$/.test(arg))throw Error('Supply a dedicated service domain');
  mkdirSync(root,{recursive:true,mode:0o700});
  mkdirSync(join(root,'registry'),{mode:0o700});
  const config={domain:arg,database:join(root,'registry','registry.sqlite'),capacity:3,network:'lazyedit-hosted',workerImage:'lazyedit-workspace:local',workerMemory:'8g',workerCPUs:2};
  writeFileSync(configPath,JSON.stringify(config,null,2));
  writeFileSync(join(root,'registry','gateway.json'),JSON.stringify({...config,database:'/registry/registry.sqlite'},null,2));
  const compose={name:'lazyedit-hosted',services:{gateway:{image:'lazyedit-gateway:local',user:'1000:1000',init:true,restart:'unless-stopped',read_only:true,cap_drop:['ALL'],security_opt:['no-new-privileges:true'],mem_limit:'256m',cpus:0.5,pids_limit:64,ports:['127.0.0.1:18980:8080'],volumes:[`${join(root,'registry')}:/registry`],command:['node','hosted/gateway.mjs','/registry/gateway.json'],networks:['front']},
    provisioner:{image:'lazyedit-provisioner:local',user:'1000:1000',group_add:[String(statSync('/var/run/docker.sock').gid)],init:true,restart:'unless-stopped',network_mode:'none',mem_limit:'256m',cpus:0.5,pids_limit:64,volumes:[`${root}:${root}`,'/var/run/docker.sock:/var/run/docker.sock'],command:['node','hosted/provision-loop.mjs',root]}},networks:{front:{name:config.network}}};
  writeFileSync(join(root,'compose.json'),JSON.stringify(compose,null,2));
  new Registry(config.database,config.domain,config.capacity).db.close();
  console.log('Initialized private configuration. Build images, then docker compose -f '+join(root,'compose.json')+' up -d');
  process.exit(0);
}
const config=JSON.parse(readFileSync(configPath)), registry=new Registry(config.database,config.domain,config.capacity);
if(command==='invite'){console.log(registry.invite());}
else if(command==='status'){console.table(registry.db.prepare('SELECT w.id,u.username,w.status FROM workspaces w JOIN users u ON u.id=w.owner').all());}
else if(command==='retry'){
  if(!/^[a-z0-9-]{24}$/.test(arg||''))throw Error('Supply workspace ID');
  registry.db.prepare("UPDATE workspaces SET status='pending' WHERE id=? AND status IN ('failed','provisioning')").run(arg);
} else if(command==='provision'){
    const rows=registry.db.prepare("SELECT w.*,u.username,u.password FROM workspaces w JOIN users u ON u.id=w.owner WHERE w.status='pending' OR (w.status='provisioning' AND w.lease<?) ORDER BY w.created").all(Date.now());
    for(const row of rows){
      if(!/^[a-z0-9-]{24}$/.test(row.id))throw Error('Invalid registry workspace ID');
      const claimed=registry.db.prepare("UPDATE workspaces SET status='provisioning',lease=? WHERE id=? AND (status='pending' OR (status='provisioning' AND lease<?)) RETURNING id").get(Date.now()+300000,row.id,Date.now());
      if(!claimed)continue;
      try{
        const dir=join(root,'workspaces',row.id);mkdirSync(dir,{recursive:true});
        if(!existsSync(join(dir,'db_password')))writeFileSync(join(dir,'db_password'),secret());
        writeFileSync(join(dir,'account.json'),JSON.stringify({...row,host:registry.host(row)}));
        // Docker's PostgreSQL image drops privileges before reading its secret.
        chmodSync(join(dir,'db_password'),0o644);
        if(!existsSync(join(dir,'providers.env')))writeFileSync(join(dir,'providers.env'),existsSync(join(root,'providers.env'))?readFileSync(join(root,'providers.env')):'# Per-workspace AI/SMTP keys. Never copy the live owner .env.\n');
        const compose=join(dir,'compose.json');writeFileSync(compose,JSON.stringify(workspaceCompose(row,config,dir),null,2));
        const result=spawnSync('docker',['compose','-f',compose,'up','-d','--wait','--wait-timeout','180'],{stdio:'inherit'});
        if(result.status!==0)throw Error('Workspace failed health checks; inspect its Docker logs');
        registry.db.prepare("UPDATE workspaces SET status='ready' WHERE id=?").run(row.id);
        console.log('Ready:',registry.host(row));
      }catch(e){registry.db.prepare("UPDATE workspaces SET status='failed' WHERE id=?").run(row.id);console.error(row.id,e.message);process.exitCode=1;}
    }
}else throw Error('Unknown command');
registry.db.close();
