#!/usr/bin/env python
"""Generate public UI dictionaries with the configured existing text provider.

No media, transcripts, credentials or user data are sent. Review dictionaries
before release. Existing complete dictionaries are reused.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shlex
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lazyedit.openai_request_json import OpenAIRequestJSONBase

LANGUAGES = {'zh-Hans':'Simplified Chinese','zh-Hant':'Traditional Chinese','ja':'Japanese','ko':'Korean','vi':'Vietnamese','ar':'Arabic','fr':'French','es':'Spanish','de':'German','ru':'Russian'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'studio/locales/en.json')
    parser.add_argument('--output', type=Path, default=ROOT/'studio/locales')
    parser.add_argument('--languages', default=','.join(LANGUAGES))
    args = parser.parse_args()
    # Read data, never source shell code or emit private configuration.
    for line in (ROOT/'.env').read_text().splitlines():
        key, sep, value = line.removeprefix('export ').partition('=')
        if sep and re.fullmatch(r'[A-Z][A-Z0-9_]*', key.strip()) and not key.strip() in os.environ:
            parsed = shlex.split(value, comments=True)
            if len(parsed) == 1:
                os.environ[key.strip()] = parsed[0]
    source = json.loads(args.source.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    def translate(code):
        target = args.output/(code+'.json')
        existing = json.loads(target.read_text()) if target.exists() else {}
        missing = {k:v for k,v in source.items() if k not in existing}
        if not missing:
            return code+' reused'
        client = OpenAIRequestJSONBase(api_provider='deepseek' if os.getenv('DEEPSEEK_API_KEY') else 'openai', use_cache=False)
        message = 'Translate these video editing/login/publishing UI strings into '+LANGUAGES[code]+'. Return one JSON object with exactly the same keys and translated string values. Preserve {{placeholders}}, numbers, platform/brand names, units, and newlines. Use natural concise UI wording. No commentary.\n'+json.dumps(missing,ensure_ascii=False)
        options = {'extra_body': {'thinking': {'type': 'disabled'}}} if client.api_provider == 'deepseek' else {}
        reply = client.client.with_options(timeout=180, max_retries=1).chat.completions.create(model=client.model, messages=[{'role':'user','content':message}], response_format={'type':'json_object'},max_tokens=18000,**options)
        content = reply.choices[0].message.content or ''
        # Some configured providers wrap JSON in Markdown despite JSON mode.
        if content.startswith('```'):
            content = re.sub(r'^```(?:json)?\s*|\s*```$', '', content).strip()
        if not content:
            raise ValueError('Provider returned no translation: '+code+' ('+str(reply.choices[0].finish_reason)+')')
        data = json.loads(content)
        if set(data) != set(missing) or any(not isinstance(v,str) or not v for v in data.values()):
            raise ValueError('Translation dictionary has missing or invalid entries: '+code)
        for key,value in missing.items():
            if sorted(re.findall(r'\{\{\w+\}\}',value)) != sorted(re.findall(r'\{\{\w+\}\}',data[key])):
                raise ValueError('Placeholder changed: '+code)
        existing.update(data)
        target.write_text(json.dumps({k:existing[k] for k in source},ensure_ascii=False,indent=2)+'\n')
        return code+' complete ('+str(len(existing))+' strings)'
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(translate, args.languages.split(',')):
            print(result, flush=True)

if __name__ == '__main__':
    main()
