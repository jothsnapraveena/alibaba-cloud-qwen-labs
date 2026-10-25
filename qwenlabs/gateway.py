"""Thread-safe admission, retry and circuit controls around a provider transport."""
import json
import os
import random
import threading
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

class Rejected(RuntimeError): pass
class BudgetExceeded(RuntimeError): pass

class Budget:
    """Per-workflow network-attempt budget, shared across roles and retries."""
    def __init__(self,limit=6):
        if limit<1: raise ValueError('limit must be positive')
        self.limit,self.used=limit,0
        self.lock=threading.Lock()
    def consume(self):
        with self.lock:
            if self.used>=self.limit: raise BudgetExceeded('Model attempt budget exhausted')
            self.used+=1

class ModelStudio:
    def __init__(self):
        self.base=os.environ.get('DASHSCOPE_BASE_URL','').rstrip('/')
        self.key=os.environ.get('DASHSCOPE_API_KEY','')
        parsed=urlparse(self.base)
        if parsed.scheme!='https' or not (parsed.hostname or '').endswith('.aliyuncs.com') or not self.key or '{' in self.base or 'YOUR_' in self.base:
            raise ValueError('Configure a real workspace endpoint and regional API key')
        self.model=os.environ.get('QWEN_MODEL','qwen-plus')
    def __call__(self,payload,timeout):
        payload=dict(payload)
        route=payload.pop('_route','chat/completions')
        if route not in ('chat/completions','embeddings'): raise ValueError('Unsupported route')
        payload.setdefault('model',self.model)
        request=Request(self.base+'/'+route,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+self.key})
        with urlopen(request,timeout=timeout) as response:
            return json.load(response)

class FixtureTransport:
    """Deterministic model-shaped fixtures. No claims of semantic model behavior."""
    def __call__(self,payload,timeout):
        system=payload['messages'][0]['content']
        if system.startswith('PLANNER'):
            text=json.dumps({'query':'Model Studio endpoint region API key','top_k':3})
        elif system.startswith('WRITER'):
            text=json.dumps({'answer':'Match your API key region to your workspace endpoint.','citations':['studio-region']})
        elif system.startswith('REVIEWER'):
            text=json.dumps({'decision':'accept','reason':'Fixture review, factual quality has not been evaluated.'})
        else:
            text='Offline fixture: inspect the cited evidence before acting.'
        return {'choices':[{'message':{'role':'assistant','content':text}}],'usage':{'prompt_tokens':0,'completion_tokens':0},'fixture':True}

class Gateway:
    def __init__(self,transport,concurrency=3,attempts=3,failure_threshold=3,cooldown=5,clock=time.monotonic,sleep=time.sleep,rng=None):
        if min(concurrency,attempts,failure_threshold)<1 or cooldown<0: raise ValueError('Invalid gateway limits')
        self.transport,self.attempts=transport,attempts
        self.slots=threading.BoundedSemaphore(concurrency)
        self.threshold,self.cooldown=failure_threshold,cooldown
        self.clock,self.sleep=clock,sleep
        self.rng=rng or random.Random()
        self.lock=threading.Lock()
        self.failures=0
        self.open_until=0
        self.probing=False
        self.events=[]
    def _enter_circuit(self):
        with self.lock:
            if self.open_until:
                if self.clock()<self.open_until or self.probing: raise Rejected('Circuit open')
                self.probing=True
    def request(self,payload,budget=None,deadline=10):
        if deadline<=0: raise ValueError('deadline must be positive')
        budget=budget or Budget()
        started=self.clock(); end=started+deadline
        if not self.slots.acquire(timeout=deadline): raise Rejected('Admission deadline exceeded')
        outcome='error'; network_attempts=0; entered=False
        try:
            self._enter_circuit()
            entered=True
            for attempt in range(self.attempts):
                remaining=end-self.clock()
                if remaining<=0: raise TimeoutError('Request deadline exceeded')
                budget.consume(); network_attempts+=1
                try:
                    result=self.transport(payload,remaining)
                    if self.clock()>end: raise TimeoutError('Transport exceeded deadline')
                    with self.lock:
                        self.failures=0; self.open_until=0; self.probing=False
                    outcome='ok'
                    return result
                except (HTTPError,URLError,TimeoutError) as error:
                    transient=not isinstance(error,HTTPError) or error.code in (429,500,502,503,504)
                    if not transient: raise
                    delay=self.rng.uniform(0,min(2**attempt,2))
                    if isinstance(error,HTTPError) and error.headers:
                        try: delay=max(delay,float(error.headers.get('Retry-After','0')))
                        except ValueError: pass  # HTTP-date Retry-After is outside this teaching subset.
                    if attempt+1==self.attempts or self.clock()+delay>=end: raise
                    self.sleep(delay)
            raise RuntimeError('Unreachable')
        except Exception:
            with self.lock:
                if network_attempts:
                    self.failures+=1
                    if self.failures>=self.threshold: self.open_until=self.clock()+self.cooldown
                if entered: self.probing=False
            raise
        finally:
            with self.lock:
                self.events.append({'trace_id':str(uuid.uuid4()),'elapsed_ms':round((self.clock()-started)*1000,3),'outcome':outcome,'attempts':network_attempts})
                del self.events[:-1000]
            self.slots.release()
    def text(self,system,user,budget=None):
        payload={'messages':[{'role':'system','content':system},{'role':'user','content':user}],'max_tokens':512}
        response=self.request(payload,budget)
        return response['choices'][0]['message']['content']
    def embeddings(self,texts,budget=None):
        if not texts: return []
        response=self.request({'_route':'embeddings','model':os.environ.get('QWEN_EMBED_MODEL','text-embedding-v4'),'input':texts,'dimensions':256,'encoding_format':'float'},budget,deadline=30)
        rows=sorted(response['data'],key=lambda d:d['index'])
        if [r['index'] for r in rows]!=list(range(len(texts))): raise ValueError('Embedding indices mismatch')
        vectors=[r['embedding'] for r in rows]
        if any(len(v)!=256 for v in vectors): raise ValueError('Expected 256-dimensional vectors')
        return vectors
