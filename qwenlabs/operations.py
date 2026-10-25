"""Bounded HTTP serving, tenant authentication, privacy-aware metrics and load tests."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import os
import threading
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from .platform import search

class Metrics:
    def __init__(self): self.lock=threading.Lock(); self.completed=0; self.errors=0; self.durations=[]
    def record(self,status,duration):
        with self.lock:
            self.completed+=1; self.errors+=int(status>=400)
            self.durations.append(duration); del self.durations[:-1000]
    def snapshot(self):
        with self.lock: return {'requests':self.completed,'errors':self.errors,'recent_samples':len(self.durations),'latency_ms_p95':pct(self.durations,.95) if self.durations else None}

def pct(values,q): return sorted(values)[max(0,math.ceil(len(values)*q)-1)]

class BoundedServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,address,handler,workers=4):
        self.admission=threading.BoundedSemaphore(workers)
        self.metrics=Metrics()
        super().__init__(address,handler)
    def process_request(self,request,address):
        if not self.admission.acquire(blocking=False):
            try: request.sendall(b'HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
            finally:
                self.metrics.record(503,0); self.shutdown_request(request)
            return
        try: super().process_request(request,address)
        except Exception:
            self.admission.release(); raise
    def process_request_thread(self,request,address):
        try: super().process_request_thread(request,address)
        finally: self.admission.release()

def handler(index,keys):
    if not keys or any(not key or not tenant for key,tenant in keys.items()): raise ValueError('Nonempty API key to tenant mapping required')
    class API(BaseHTTPRequestHandler):
        def setup(self):
            super().setup(); self.connection.settimeout(3)
        def log_message(self,*args): pass  # Do not log paths, bearer tokens or bodies.
        def reply(self,code,value):
            payload=json.dumps(value).encode()
            self.send_response(code); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(payload))); self.end_headers(); self.wfile.write(payload)
        def tenant(self): return keys.get(self.headers.get('Authorization','').removeprefix('Bearer '))
        def do_GET(self):
            if self.path in ('/live','/ready'):
                # ready checks storage; live only checks the HTTP process.
                try:
                    if self.path=='/ready':
                        with index.connect() as db: db.execute('SELECT 1 FROM chunks LIMIT 1').fetchone()
                    self.reply(200,{'status':'ok'})
                except Exception: self.reply(503,{'status':'not_ready'})
            elif self.path=='/metrics' and self.tenant(): self.reply(200,self.server.metrics.snapshot())
            else: self.reply(404,{'error':'not_found'})
        def do_POST(self):
            started=time.perf_counter(); status=500
            try:
                tenant=self.tenant()
                if not tenant: status=401; return self.reply(status,{'error':'unauthorized'})
                if self.path!='/search': status=404; return self.reply(status,{'error':'not_found'})
                try: length=int(self.headers.get('Content-Length','0'))
                except ValueError: length=0
                if not 0<length<=16384: status=413; return self.reply(status,{'error':'invalid_body_size'})
                value=json.loads(self.rfile.read(length))
                if not isinstance(value,dict) or set(value)-{'query','k'} or not isinstance(value.get('query'),str) or not 1<=len(value['query'])<=300 or type(value.get('k',3)) is not int or not 1<=value.get('k',3)<=5:
                    status=400; return self.reply(status,{'error':'invalid_query'})
                rows=search(index,tenant,value['query'],value.get('k',3))
                status=200; self.reply(status,{'results':[{'id':r['source'],'text':r['text'],'score':r['score']} for r in rows]})
            except (ValueError,UnicodeDecodeError): status=400; self.reply(status,{'error':'invalid_json'})
            except Exception: status=500; self.reply(status,{'error':'internal_error'})
            finally: self.server.metrics.record(status,(time.perf_counter()-started)*1000)
    return API

def benchmark(operation,requests=100,workers=8):
    if not 1<=requests<=10000 or not 1<=workers<=64: raise ValueError('Invalid load limits')
    def task(i):
        start=time.perf_counter()
        try: operation(i); return True,(time.perf_counter()-start)*1000
        except Exception: return False,(time.perf_counter()-start)*1000
    started=time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        outcomes=list(pool.map(task,range(requests)))
    seconds=time.perf_counter()-started
    successes=[ms for ok,ms in outcomes if ok]
    return {'requests':requests,'successes':len(successes),'errors':requests-len(successes),'error_rate':1-len(successes)/requests,'throughput_rps':requests/seconds,'successful_latency_ms':{name:pct(successes,q) if successes else None for name,q in [('p50',.5),('p95',.95),('p99',.99)]},'slo_pass':len(successes)/requests>=.99 and bool(successes) and pct(successes,.95)<500}

def main():
    import argparse
    from .platform import Index, sample_index
    parser=argparse.ArgumentParser(description='Local retrieval API and concurrent HTTP load client')
    parser.add_argument('action',choices=['serve','load'])
    parser.add_argument('--db',default='results/platform.sqlite')
    parser.add_argument('--seed-demo',action='store_true')
    parser.add_argument('--host',default='127.0.0.1'); parser.add_argument('--port',type=int,default=8080)
    parser.add_argument('--workers',type=int,default=4); parser.add_argument('--requests',type=int,default=100)
    parser.add_argument('--url',default='http://127.0.0.1:8080/search')
    args=parser.parse_args()
    if args.action=='load':
        key=os.environ['LAB_API_KEY']
        def operation(_):
            req=Request(args.url,data=b'{"query":"Model Studio API region"}',headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
            with urlopen(req,timeout=5) as response:
                if response.status!=200: raise RuntimeError('Request failed')
                json.load(response)
        print(json.dumps(benchmark(operation,args.requests,args.workers),indent=2))
    else:
        if not 1<=args.workers<=64: parser.error('--workers must be 1..64')
        from pathlib import Path
        Path(args.db).parent.mkdir(parents=True,exist_ok=True)
        index=sample_index(args.db) if args.seed_demo else Index(args.db)
        keys=json.loads(os.environ['LAB_API_KEYS_JSON'])
        if not isinstance(keys,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in keys.items()): parser.error('LAB_API_KEYS_JSON must map key strings to tenant strings')
        server=BoundedServer((args.host,args.port),handler(index,keys),args.workers)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
        finally: server.server_close()

if __name__=='__main__': main()
