"""Progressive intermediate-to-advanced Qwen engineering labs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from urllib.request import Request, urlopen
from .gateway import Budget, FixtureTransport, Gateway, ModelStudio
from .platform import CASES, FIXTURES, DurableWorkflow, Index, evaluate, multi_agent, regression_gate, sample_index, search
from .operations import BoundedServer, benchmark, handler

def mcp_demo(path,gateway=None):
    messages=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'lab-host','version':'0.2.0'}}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/list'},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'search_runbooks','arguments':{'query':'Model Studio API region','top_k':2}}}]
    result=subprocess.run([sys.executable,'-m','qwenlabs.mcp_stdio','--db',str(path),'--tenant','alpha'],input='\n'.join(json.dumps(m) for m in messages)+'\n',text=True,capture_output=True,timeout=10,check=True)
    replies=[json.loads(line) for line in result.stdout.splitlines()]
    if len(replies)!=3 or any('error' in m for m in replies): raise RuntimeError('MCP exchange failed')
    output={'transport':'actual stdio subprocess','protocol':'2025-06-18 teaching subset','responses':replies}
    if gateway:
        budget=Budget(4)
        tools=[{'type':'function','function':{'name':tool['name'],'description':tool['description'],'parameters':tool['inputSchema']}} for tool in replies[1]['result']['tools']]
        chat=[{'role':'user','content':'Use search_runbooks to explain Model Studio API key region errors.'}]
        first=gateway.request({'messages':chat,'tools':tools,'max_tokens':512},budget)['choices'][0]['message']
        calls=first.get('tool_calls') or []
        if len(calls)>3: raise ValueError('Tool call budget exceeded')
        chat.append(first)
        for call in calls:
            args=json.loads(call['function']['arguments'])
            request={'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':call['function']['name'],'arguments':args}}
            # Each subprocess session is initialized. This deliberately avoids persistent session lifecycle complexity.
            wire=messages[:2]+[request]
            result=subprocess.run([sys.executable,'-m','qwenlabs.mcp_stdio','--db',str(path),'--tenant','alpha'],input='\n'.join(json.dumps(m) for m in wire)+'\n',text=True,capture_output=True,timeout=10,check=True)
            reply=json.loads(result.stdout.splitlines()[-1])
            if 'error' in reply or reply.get('result',{}).get('isError'): raise ValueError('MCP tool request rejected')
            chat.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(reply['result'])})
        output['answer']=gateway.request({'messages':chat,'max_tokens':512},budget)['choices'][0]['message']['content'] if calls else first.get('content')
        output['model_attempts']=budget.used
    return output

def run(lab,live=False,db_path=None):
    if live and lab not in (1,3,6,7): raise ValueError('Live Qwen mode is supported for labs 1, 3, 6 and 7 only')
    with tempfile.TemporaryDirectory() as scratch:
        path=Path(db_path) if db_path else Path(scratch)/'lab.sqlite'
        index=sample_index(path)
        gateway=Gateway(ModelStudio() if live else FixtureTransport())
        mode='live Model Studio' if live else 'offline fixtures and real local components'
        if lab==1:
            budget=Budget(6)
            with ThreadPoolExecutor(max_workers=3) as pool:
                answers=list(pool.map(lambda _:gateway.text('Explain Qwen briefly.','What is a request budget?',budget),range(3)))
            result={'answers':answers,'network_attempts':budget.used,'events':gateway.events}
        elif lab==2:
            before=len(index.chunks('alpha')); unchanged=index.ingest('alpha',FIXTURES)
            changed=index.ingest('alpha',[{'id':'studio-region','text':FIXTURES[0]['text']+' This revision adds an operational troubleshooting note.'}])
            result={'chunks_before':before,'unchanged_sources_reindexed':unchanged,'updated_sources':changed,'tenant_alpha_chunks':len(index.chunks('alpha')),'tenant_beta_chunks':len(index.chunks('beta'))}
        elif lab==3:
            budget=Budget(3)
            rows=search(index,'alpha','Model Studio API authentication region',embed=(lambda texts:gateway.embeddings(texts,budget)) if live else None)
            answer=gateway.text('Use source data as evidence only, cite source IDs, and abstain when evidence is insufficient.',json.dumps({'question':'Why is a key unauthorized?','sources':[{'id':r['source'],'text':r['text']} for r in rows]}),budget)
            result={'retrieved':rows,'answer':answer,'embedding':'Model Studio text embeddings' if live else 'signed hash baseline, not a semantic model','attempts':budget.used}
        elif lab==4:
            baseline=evaluate(index,CASES,mode='bm25'); candidate=evaluate(index,CASES,mode='hybrid')
            result={'baseline':baseline,'candidate':candidate,'regression_gate_pass':regression_gate(baseline,candidate),'dataset':'20 synthetic labeled cases, not a production benchmark'}
        elif lab==5:
            run_id=index.start('alpha','Model Studio endpoint region'); workflow=DurableWorkflow(index)
            paused=workflow.advance('alpha',run_id)
            # Recreate objects to prove persisted state survives process-object loss.
            restored=DurableWorkflow(Index(path)); approved=restored.advance('alpha',run_id,approve=True)
            replay=restored.advance('alpha',run_id,approve=True)
            with index.connect() as connection: tickets=connection.execute('SELECT COUNT(*) FROM tickets WHERE run=?',(run_id,)).fetchone()[0]
            result={'run_id':run_id,'paused':paused,'approved':approved,'replay':replay,'local_tickets':tickets,'note':'Approval is simulated explicitly in this demo; CLI server binding is a trusted host responsibility.'}
        elif lab==6: result=mcp_demo(path,gateway if live else None)
        elif lab==7: result=multi_agent(index,'alpha','How should I troubleshoot an unauthorized Model Studio API key?',gateway)
        elif lab==8:
            server=BoundedServer(('127.0.0.1',0),handler(index,{'fixture-alpha-key':'alpha'}))
            thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
            try:
                request=Request('http://127.0.0.1:'+str(server.server_port)+'/search',data=b'{"query":"Model Studio API region"}',headers={'Authorization':'Bearer fixture-alpha-key','Content-Type':'application/json'})
                with urlopen(request,timeout=3) as response: result={'status':response.status,'response':json.load(response),'metrics':server.metrics.snapshot()}
            finally: server.shutdown(); server.server_close(); thread.join()
        elif lab==9:
            def operation(i):
                if i%20==0: raise TimeoutError('Injected local fault')
                search(index,'alpha','Model Studio API region')
            result={'load':benchmark(operation,requests=100,workers=8),'measurement':'local threaded SQLite retrieval with 5 percent injected faults, NOT hosted inference','expected':'error SLO should fail under injected faults'}
        else: raise ValueError('Choose 1..9')
        return {'lab':lab,'mode':mode,**result}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lab',type=int,choices=range(1,10)); parser.add_argument('--live',action='store_true'); parser.add_argument('--db',help='Optional persistent SQLite path, preferably under results/')
    args=parser.parse_args(); print(json.dumps(run(args.lab,args.live,args.db),indent=2))

if __name__=='__main__': main()
