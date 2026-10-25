"""Small educational MCP stdio server, pinned to revision 2025-06-18.
Supports initialize, initialized notification, ping, tools/list, tools/call.
No HTTP, resources, prompts, pagination or current-version conformance claim.
"""
import argparse
import json
import os
import sys
from .platform import Index, search

TOOL={'name':'search_runbooks','description':'Search runbooks within the tenant assigned by the host process.','inputSchema':{'type':'object','properties':{'query':{'type':'string','minLength':1,'maxLength':300},'top_k':{'type':'integer','minimum':1,'maximum':5}},'required':['query'],'additionalProperties':False},'annotations':{'readOnlyHint':True,'destructiveHint':False}}

class Session:
    def __init__(self,index,tenant): self.index,self.tenant,self.initialized,self.ready=index,tenant,False,False
    def handle(self,msg):
        ident=msg.get('id') if isinstance(msg,dict) else None
        def error(code,text): return {'jsonrpc':'2.0','id':ident,'error':{'code':code,'message':text}}
        if not isinstance(msg,dict) or msg.get('jsonrpc')!='2.0' or not isinstance(msg.get('method'),str): return error(-32600,'Invalid Request')
        method=msg['method']; params=msg.get('params',{})
        if not isinstance(params,dict): return error(-32602,'Invalid params')
        if 'id' not in msg:
            if method=='notifications/initialized' and self.initialized: self.ready=True
            return None
        if method=='initialize':
            if self.initialized: return error(-32600,'Already initialized')
            if params.get('protocolVersion')!='2025-06-18': return error(-32602,'Only protocol 2025-06-18 is supported in this lab')
            self.initialized=True
            value={'protocolVersion':'2025-06-18','capabilities':{'tools':{'listChanged':False}},'serverInfo':{'name':'qwen-runbooks-lab','version':'0.2.0'}}
        elif method=='ping': value={}
        elif not self.ready: return error(-32002,'Initialize session first')
        elif method=='tools/list': value={'tools':[TOOL]}
        elif method=='tools/call':
            if params.get('name')!='search_runbooks': return error(-32602,'Unknown tool')
            args=params.get('arguments',{})
            if not isinstance(args,dict) or set(args)-{'query','top_k'} or not isinstance(args.get('query'),str) or not 1<=len(args['query'])<=300 or type(args.get('top_k',3)) is not int or not 1<=args.get('top_k',3)<=5: return error(-32602,'Invalid tool arguments')
            try:
                rows=search(self.index,self.tenant,args['query'],args.get('top_k',3))
                value={'content':[{'type':'text','text':json.dumps([{'id':r['source'],'text':r['text']} for r in rows])}],'isError':False}
            except Exception:
                value={'content':[{'type':'text','text':'Search failed'}],'isError':True}
        else: return error(-32601,'Method not found')
        return {'jsonrpc':'2.0','id':ident,'result':value}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',required=True); parser.add_argument('--tenant',required=True)
    args=parser.parse_args(); session=Session(Index(args.db),args.tenant)
    for raw in sys.stdin.buffer:
        if len(raw)>65536:
            response={'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Message too large'}}
        else:
            try: response=session.handle(json.loads(raw))
            except (json.JSONDecodeError,UnicodeDecodeError): response={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Parse error'}}
        if response is not None: print(json.dumps(response),flush=True)

if __name__=='__main__': main()
