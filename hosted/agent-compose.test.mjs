import test from 'node:test';
import assert from 'node:assert/strict';
import {workspaceCompose} from './compose.mjs';
const id='a'.repeat(24);
test('direct API remains default and has no planner resources',()=>{
 const value=workspaceCompose({id},{},'/private/bootstrap');
 assert.equal(value.services.planner,undefined);
 assert.equal(value.services.worker.environment.STUDIO_AGENT_URL,undefined);
});
test('optional planner is private and cannot mount user data or publisher profiles',()=>{
 const value=workspaceCompose({id},{agentSandbox:true},'/private/bootstrap');
 const agent=value.services.planner;
 assert.equal(agent.read_only,true);
 assert.deepEqual(agent.cap_drop,['ALL']);
 assert.equal(agent.ports,undefined);
 assert.equal(agent.volumes,undefined);
 assert.equal(agent.networks.includes('front'),false);
 assert.equal(agent.networks.includes('private'),false);
 assert.deepEqual(value.networks.agent,{internal:true});
 assert.equal(value.services.worker.environment.STUDIO_AGENT_URL,'http://planner:8092');
 assert.ok(value.services.worker.volumes.includes('workspace:/state'));
});
