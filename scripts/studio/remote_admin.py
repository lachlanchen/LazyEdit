#!/usr/bin/env python
"""Run a reviewed script on the Studio edge; password is read privately, never argv."""
import argparse,json,pathlib,shlex,subprocess
p=argparse.ArgumentParser();p.add_argument('script');p.add_argument('--credentials',required=True);p.add_argument('--ssh-config',required=True);p.add_argument('--host',default='hncloud');a=p.parse_args()
c=json.loads(pathlib.Path(a.credentials).read_text());content=pathlib.Path(a.script).read_text()
result=subprocess.run(['ssh','-F',a.ssh_config,a.host,'sudo -S -p "" /bin/bash -c '+shlex.quote(content)],input=c['password']+'\n',text=True)
raise SystemExit(result.returncode)
