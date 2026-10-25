"""Run: python -m qwenlabs.run 1 [--live]. Offline by default."""
import argparse
import json
import time
import uuid
from .client import Qwen
from .core import DOCUMENTS, chunks, retrieve, grounded_prompt, validate_ticket, execute_tool, retry, percentile

TOOL = {'type':'function','function':{'name':'lookup_service','description':'Look up one Alibaba Cloud service in a small local glossary.','parameters':{'type':'object','properties':{'service':{'type':'string','enum':['ecs','oss','studio']}},'required':['service'],'additionalProperties':False}}}

def run(lab, live=False):
    client=Qwen(live)
    if lab==1:
        prompt='Explain Alibaba Cloud Model Studio to a Python developer in three sentences.'
        return {'mode':'live' if live else 'offline fixture','answer':client.answer(prompt) if live else 'Model Studio exposes hosted Qwen inference. Configure your regional endpoint and API key. This response is a fixture, not a cloud result.'}
    if lab==2:
        text=client.answer('Classify: My invoice is incorrect. Return only JSON with category (billing, technical, account) and priority (low, medium, high).') if live else '{"category":"billing","priority":"medium"}'
        return validate_ticket(text)
    if lab==3:
        question='How do I configure the Model Studio API key region?'
        docs=retrieve(question)
        return {'chunks':chunks(' '.join(d['text'] for d in DOCUMENTS)), 'retrieved':docs, 'answer':client.answer(grounded_prompt(question,docs)) if live else 'Inspect retrieved IDs and scores. Add --live for Qwen generation.'}
    if lab==4:
        cases=[('virtual servers','ecs'),('objects buckets','oss'),('Qwen API region','studio'),('buckets credentials','oss')]
        rows=[{'query':q,'expected':expected,'actual':[d['id'] for d in retrieve(q,k=1)]} for q,expected in cases]
        return {'dataset':'four synthetic teaching cases, not a benchmark','hit_at_1':sum(r['expected'] in r['actual'] for r in rows)/len(rows),'cases':rows}
    if lab==5:
        if not live:
            return {'mode':'offline tool fixture','result':execute_tool('lookup_service',{'service':'oss'})}
        messages=[{'role':'user','content':'Use lookup_service to explain OSS.'}]
        first=client.chat(messages,tools=[TOOL])['choices'][0]['message']
        calls=first.get('tool_calls',[])
        if len(calls)>3:
            raise ValueError('Tool call budget exceeded')
        if not calls:
            return {'answer':first.get('content'),'tool_calls':0}
        messages.append(first)
        for call in calls:
            result=execute_tool(call['function']['name'],json.loads(call['function']['arguments']))
            messages.append({'role':'tool','tool_call_id':call['id'],'content':result})
        # No tools on the final call: at most two model calls.
        return {'answer':client.chat(messages)['choices'][0]['message']['content'],'tool_calls':len(calls)}
    if lab==6:
        start=time.perf_counter()
        usage=None
        if live:
            response=client.chat([{'role':'user','content':'Explain Qwen in one sentence.'}])
            usage=response.get('usage')
        else:
            retrieve('Qwen region')
        return {'trace_id':str(uuid.uuid4()),'mode':'live' if live else 'local retrieval only','operation':'chat' if live else 'retrieve','duration_ms':round((time.perf_counter()-start)*1000,3),'model':client.model if live else None,'usage':usage,'content_logged':False}
    if lab==7:
        attempts=[]
        def flaky():
            attempts.append(1)
            if len(attempts)<3:
                raise TimeoutError('Synthetic transient failure')
            return 'recovered'
        waits=[]
        return {'result':retry(flaky,sleep=waits.append),'attempts':len(attempts),'scheduled_delays_seconds':waits,'note':'Synthetic fault injection. Never retry side-effecting tools without idempotency.'}
    if lab==8:
        start=time.perf_counter()
        draft=client.answer('Draft a two-sentence explanation of why Qwen RAG needs citations.') if live else 'Qwen RAG should cite retrieved source IDs. This lets readers inspect the evidence.'
        # Deterministic review keeps the example bounded and inspectable.
        review={'mentions_citations':'cit' in draft.lower(),'requires_human_review':True}
        return {'draft':draft,'review':review,'steps':['draft','deterministic review','human review'],'duration_ms':round((time.perf_counter()-start)*1000,3),'note':'A small governed workflow, not an autonomous multi-agent framework.'}
    if lab==9:
        durations=[]
        for _ in range(5):
            start=time.perf_counter()
            if live:
                client.answer('Reply with the word ready.')
            else:
                retrieve('Qwen region')
            durations.append((time.perf_counter()-start)*1000)
        return {'mode':'live sequential chat' if live else 'local retrieval microbenchmark','samples':len(durations),'p50_ms':percentile(durations,.5),'p95_ms':percentile(durations,.95),'raw_ms':durations,'note':'Five samples cannot establish production capacity. No performance claims implied.'}
    raise ValueError('Choose lab 1 through 9')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lab',type=int,choices=range(1,10))
    parser.add_argument('--live',action='store_true',help='Send requests to your configured Model Studio endpoint; charges may apply')
    args=parser.parse_args()
    if args.live and args.lab in (4,7):
        parser.error('This lab is entirely local; omit --live')
    print(json.dumps(run(args.lab,args.live),indent=2))

if __name__=='__main__':
    main()
