#!/usr/bin/env python
"""Prepare only LazyEdit's own Google subscription names/benefits as drafts.

Uses an already authenticated visible store tab. Never activates a base plan,
changes another app, saves passwords, or submits a release.
"""
import argparse
import json
import time
from cdp import Tab
from store_products import PLANS, MINUTES

APP_PATH = "/console/u/0/developers/6157557679644496686/app/4975166991517752718"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=9485)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    tab = Tab(args.port, args.target)
    try:
        current = tab.evaluate("({origin:location.origin,path:location.pathname})")
        if current["origin"] != "https://play.google.com" or not current["path"].startswith(APP_PATH+"/"):
            raise RuntimeError("Select LazyEdit's own Google Play tab first")

        def wait(expression):
            end = time.monotonic()+35
            while time.monotonic() < end:
                try:
                    value = tab.evaluate(expression)
                except RuntimeError as error:
                    # Read-only polling may overlap document replacement.
                    if not any(v in str(error) for v in ('Uncaught', 'Execution context', 'Cannot find context')):
                        raise
                    value = None
                if value:
                    return value
                time.sleep(0.25)
            raise RuntimeError("Store UI did not reach the expected draft state")

        def navigate(path, ready=None):
            tab.call("Page.navigate", {"url": "https://play.google.com"+path})
            condition="location.pathname==="+json.dumps(path)+"&&!!document.body"+("&&("+ready+")" if ready else "")
            try:
                wait(condition)
            except RuntimeError:
                # Recover a stuck read-only page once. Never replay Create/Save.
                tab.call("Page.reload", {"ignoreCache": False})
                wait(condition)

        def click(label, dialog=False):
            scope = "document.querySelector('[role=dialog]')" if dialog else "document"
            js = f"(()=>{{const root={scope};if(!root)return false;const e=Array.from(root.querySelectorAll('button,[role=button]')).find(e=>e.getClientRects().length&&e.innerText.trim()==={json.dumps(label)});if(!e||e.getAttribute('aria-disabled')==='true')return false;e.click();return true;}})()"
            wait(js.replace('e.click();return true;', 'return true;'))
            if not tab.evaluate(js):
                raise RuntimeError("Draft action was not accepted; inspect before retrying")

        def fill(selector, value):
            if not tab.evaluate(f"(()=>{{const e=document.querySelector({json.dumps(selector)});if(!e)return false;Object.getOwnPropertyDescriptor(e.tagName==='INPUT'?HTMLInputElement.prototype:HTMLTextAreaElement.prototype,'value').set.call(e,{json.dumps(value)});e.dispatchEvent(new Event('input',{{bubbles:true}}));e.dispatchEvent(new Event('change',{{bubbles:true}}));return true;}})()"):
                raise RuntimeError("Expected draft field is missing")

        receipts = []
        for plan, name, price, _ in PLANS:
            product = f"art.lazying.lazyedit.{plan}.monthly"
            title = "LazyEdit "+name
            navigate(APP_PATH+"/subscriptions", "document.body?.innerText.includes('Name and ID')&&document.body?.innerText.includes('Show rows:')")
            # Play renders the Create button before its async product rows.
            # This app's Starter draft already exists; wait for the loaded
            # table before interpreting a missing ID as a new product.
            wait("document.body?.innerText.includes('Name and ID')&&document.body?.innerText.includes('Show rows:')")
            if not tab.evaluate("document.body?.innerText.includes("+json.dumps(product)+")"):
                click("Create subscription")
                wait("!!document.querySelector('[role=dialog] input[aria-label=\"Product ID\"]')")
                fill('input[aria-label="Product ID"]', product)
                fill('input[aria-label="Name"]', title)
                click("Create", True)
                wait("location.pathname==="+json.dumps(APP_PATH+"/subscriptions/s/"+product))
            navigate(APP_PATH+"/subscriptions/s/"+product)
            click("Edit subscription details")
            wait("location.pathname.endsWith('/details')&&!!document.querySelector('textarea[aria-label=Description]')")
            state = tab.evaluate("({description:document.querySelector('textarea[aria-label=Description]').value,benefits:Array.from(document.querySelectorAll('input[aria-label=Benefits]')).map(e=>e.value),name:Array.from(document.querySelectorAll('input')).find(e=>e.required)?.value})")
            benefit = f"{MINUTES[plan]} source-video minutes per UTC month"
            description = f"{MINUTES[plan]} source-video minutes per UTC calendar month. Each requested processing run counts once; completed runs can be reused. Unused time does not roll over."
            if state['name'] != title or state['description'] not in ('', description) or any(v and v!=benefit for v in state['benefits']):
                raise RuntimeError("Preserve an existing different product description")
            if state['description'] != description or benefit not in state['benefits']:
                if not state['benefits']:
                    click("add\nAdd benefit")
                fill('input[aria-label=Benefits]', benefit)
                fill('textarea[aria-label=Description]', description)
                click("Save changes")
                wait("document.body?.innerText.includes('Your changes have been saved')")
            receipts.append({"productId": product, "requestedUSD": price,
                "processingMinutes": MINUTES[plan], "draftBenefitsSaved": True,
                "basePlanActivated": False})
        navigate(APP_PATH+"/subscriptions")
        wait("document.body?.innerText.includes("+json.dumps(receipts[-1]['productId'])+")")
        print(json.dumps({"app": "art.lazying.lazyedit", "products": receipts,
            "billingActivated": False, "reviewSubmitted": False}, indent=2))
    finally:
        tab.close()


if __name__ == "__main__":
    main()
