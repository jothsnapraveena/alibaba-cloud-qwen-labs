from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from qwenlabs.gateway import Budget, BudgetExceeded, FixtureTransport, Gateway, Rejected
from qwenlabs.platform import CASES, FIXTURES, DurableWorkflow, Index, evaluate, multi_agent, regression_gate, sample_index, search
from qwenlabs.mcp_stdio import Session
from qwenlabs.operations import BoundedServer, benchmark, handler
from qwenlabs.run import mcp_demo

class Storage(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.path=Path(self.temp.name)/'index.sqlite'; self.index=sample_index(self.path)
    def tearDown(self): self.temp.cleanup()
    def test_reingest_is_idempotent(self):
        original=self.index.chunks('alpha')
        self.assertEqual(self.index.ingest('alpha',FIXTURES),0)
        self.assertEqual(self.index.chunks('alpha'),original)
    def test_chunk_configuration_invalidates_index(self):
        self.assertEqual(self.index.ingest('alpha',FIXTURES,size=8,overlap=2),len(FIXTURES))
        self.assertGreater(len(self.index.chunks('alpha')),len(FIXTURES))
    def test_replacement_removes_stale_chunks(self):
        before={r['id'] for r in self.index.chunks('alpha') if r['source']=='studio-region'}
        self.index.ingest('alpha',[{'id':'studio-region','text':'new replacement'}])
        after={r['id'] for r in self.index.chunks('alpha') if r['source']=='studio-region'}
        self.assertFalse(before & after)
    def test_tenant_filter_before_embedding(self):
        seen=[]
        from qwenlabs.platform import HashEmbedding
        def embed(texts): seen.extend(texts); return HashEmbedding()(texts)
        rows=search(self.index,'alpha','confidential beta-only record',embed=embed)
        self.assertTrue(all(r['tenant']=='alpha' for r in rows))
        self.assertFalse(any('restricted financial' in t for t in seen))
    def test_delete_is_tenant_scoped(self):
        self.index.ingest('beta',[FIXTURES[0]])
        self.index.delete('alpha','studio-region')
        self.assertNotIn('studio-region',[r['source'] for r in self.index.chunks('alpha')])
        self.assertIn('studio-region',[r['source'] for r in self.index.chunks('beta')])
    def test_invalid_batch_does_not_partial_write(self):
        with self.assertRaises(ValueError): self.index.ingest('alpha',[{'id':'fresh','text':'fine'},{'id':'bad','text':None}])
        self.assertNotIn('fresh',[r['source'] for r in self.index.chunks('alpha')])
    def test_stale_worker_cannot_commit_side_effect(self):
        run=self.index.start('alpha','region'); rev,state=self.index.load('alpha',run)
        self.index.save('alpha',run,rev,state)
        with self.assertRaises(RuntimeError): self.index.save('alpha',run,rev,state,ticket={'bad':True})
        with self.index.connect() as db: self.assertEqual(db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0],0)
    def test_approval_pause_restart_and_replay(self):
        run=self.index.start('alpha','region'); flow=DurableWorkflow(self.index)
        self.assertEqual(flow.advance('alpha',run)[1]['phase'],'awaiting_approval')
        self.assertEqual(flow.advance('alpha',run)[1]['phase'],'awaiting_approval')
        resumed=DurableWorkflow(Index(self.path)); resumed.advance('alpha',run,approve=True); resumed.advance('alpha',run,approve=True)
        with self.index.connect() as db: self.assertEqual(db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0],1)
        with self.assertRaises(KeyError): self.index.load('beta',run)
    def test_regression_gate_detects_degradation(self):
        report=evaluate(self.index,CASES)
        self.assertTrue(regression_gate(report,report))
        self.assertFalse(regression_gate(report,{**report,'recall':0}))
        self.assertLessEqual(report['ndcg_bootstrap_95'][0],report['ndcg_bootstrap_95'][1])
    def test_multi_role_chain_has_three_model_calls(self):
        result=multi_agent(self.index,'alpha','region',Gateway(FixtureTransport()))
        self.assertEqual(result['attempts'],3)
        self.assertEqual(result['status'],'human_review')
    def test_writer_unknown_citation_is_rejected(self):
        class Bad(FixtureTransport):
            def __call__(self,payload,timeout):
                if payload['messages'][0]['content'].startswith('WRITER'):
                    return {'choices':[{'message':{'content':json.dumps({'answer':'invented','citations':['beta-secret']})}}]}
                return super().__call__(payload,timeout)
        with self.assertRaises(ValueError): multi_agent(self.index,'alpha','region',Gateway(Bad()))
    def test_mcp_process_transport_roundtrip(self):
        result=mcp_demo(self.path)
        self.assertEqual([m['id'] for m in result['responses']],[1,2,3])
        self.assertIn('result',result['responses'][2])
    def test_qwen_to_mcp_bridge_preserves_tool_message(self):
        calls=[]
        def model(payload,timeout):
            calls.append(payload)
            if 'tools' in payload:
                return {'choices':[{'message':{'role':'assistant','content':None,'tool_calls':[{'id':'call-1','type':'function','function':{'name':'search_runbooks','arguments':'{"query":"Model Studio region"}'}}]}}]}
            self.assertEqual(payload['messages'][-1]['tool_call_id'],'call-1')
            self.assertEqual(payload['messages'][-1]['role'],'tool')
            return {'choices':[{'message':{'content':'Verified transport result fixture'}}]}
        result=mcp_demo(self.path,Gateway(model))
        self.assertEqual(result['model_attempts'],2)
        self.assertEqual(len(calls),2)
        self.assertEqual(result['answer'],'Verified transport result fixture')

    def test_mcp_lifecycle_and_argument_controls(self):
        s=Session(self.index,'alpha')
        def message(method,params=None): return s.handle({'jsonrpc':'2.0','id':1,'method':method,'params':params or {}})
        self.assertIn('error',message('tools/list'))
        message('initialize',{'protocolVersion':'2025-06-18'})
        self.assertIn('error',message('tools/list'))
        s.handle({'jsonrpc':'2.0','method':'notifications/initialized'})
        for args in ({'query':'region','tenant':'beta'},{'query':'region','top_k':True},{'query':''}):
            self.assertEqual(message('tools/call',{'name':'search_runbooks','arguments':args})['error']['code'],-32602)
    def test_api_auth_and_tenant_spoofing(self):
        server=BoundedServer(('127.0.0.1',0),handler(self.index,{'test-key':'alpha'}))
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        def request(payload,token='test-key'):
            req=Request('http://127.0.0.1:'+str(server.server_port)+'/search',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+token})
            with urlopen(req,timeout=3) as response: return json.load(response)
        try:
            for payload,token,status in [({'query':'region'},'bad',401),({'query':'region','tenant':'beta'},'test-key',400),({'query':'region','k':True},'test-key',400)]:
                with self.assertRaises(HTTPError) as err: request(payload,token)
                self.assertEqual(err.exception.code,status)
            result=request({'query':'confidential beta-only record'})
            self.assertNotIn('beta-secret',[r['id'] for r in result['results']])
        finally: server.shutdown(); server.server_close(); thread.join()
    def test_api_overload_rejects_before_spawning_worker(self):
        server=BoundedServer(('127.0.0.1',0),handler(self.index,{'test-key':'alpha'}),workers=1)
        self.assertTrue(server.admission.acquire(False))
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            with self.assertRaises(HTTPError) as err: urlopen('http://127.0.0.1:'+str(server.server_port)+'/live',timeout=3)
            self.assertEqual(err.exception.code,503)
        finally: server.admission.release(); server.shutdown(); server.server_close(); thread.join()

class GatewayTests(unittest.TestCase):
    def test_budget_counts_retries_not_only_logical_calls(self):
        calls=[]
        def transport(payload,timeout): calls.append(1); raise TimeoutError('fixture')
        gateway=Gateway(transport,attempts=3,sleep=lambda _:None)
        budget=Budget(2)
        with self.assertRaises(BudgetExceeded): gateway.request({},budget)
        self.assertEqual(len(calls),2)
    def test_non_transient_auth_error_is_not_retried(self):
        calls=[]
        def transport(payload,timeout): calls.append(1); raise HTTPError('',401,'unauthorized',{},None)
        with self.assertRaises(HTTPError): Gateway(transport,sleep=lambda _:None).request({})
        self.assertEqual(len(calls),1)
    def test_retry_after_is_honored(self):
        calls=[]; waits=[]
        def transport(payload,timeout):
            calls.append(1)
            if len(calls)==1: raise HTTPError('',429,'throttled',{'Retry-After':'2'},None)
            return {'ok':True}
        gateway=Gateway(transport,sleep=waits.append)
        self.assertEqual(gateway.request({}),{'ok':True})
        self.assertEqual(waits,[2.0])
    def test_circuit_open_and_half_open_recovery(self):
        clock=[0]; calls=[]
        def transport(payload,timeout):
            calls.append(1)
            if len(calls)==1: raise TimeoutError()
            return {'ok':True}
        gateway=Gateway(transport,attempts=1,failure_threshold=1,cooldown=5,clock=lambda:clock[0])
        with self.assertRaises(TimeoutError): gateway.request({})
        with self.assertRaises(Rejected): gateway.request({})
        clock[0]=6
        self.assertEqual(gateway.request({}),{'ok':True})
        self.assertEqual(len(calls),2)
    def test_admission_limit_holds_under_concurrency(self):
        lock=threading.Lock(); counts={'active':0,'peak':0}
        def transport(payload,timeout):
            with lock: counts['active']+=1; counts['peak']=max(counts['peak'],counts['active'])
            time.sleep(.01)
            with lock: counts['active']-=1
            return {}
        gateway=Gateway(transport,concurrency=2)
        with ThreadPoolExecutor(max_workers=8) as pool: list(pool.map(lambda _:gateway.request({}),range(16)))
        self.assertEqual(counts['peak'],2)
    def test_metrics_do_not_record_prompt_content(self):
        gateway=Gateway(FixtureTransport()); gateway.text('secret instruction','private patient data')
        serialized=json.dumps(gateway.events)
        self.assertNotIn('patient',serialized); self.assertNotIn('instruction',serialized)
    def test_deadline_prevents_extra_attempt(self):
        clock=[0]; calls=[]
        def slow(payload,timeout): calls.append(1); clock[0]=11; return {}
        gateway=Gateway(slow,clock=lambda:clock[0],sleep=lambda _:None)
        with self.assertRaises(TimeoutError): gateway.request({},deadline=10)
        self.assertEqual(len(calls),1)
    def test_embedding_order_and_dimension_contract(self):
        def model(payload,timeout):
            self.assertEqual(payload['_route'],'embeddings')
            return {'data':[{'index':1,'embedding':[0.0]*256},{'index':0,'embedding':[1.0]*256}]}
        result=Gateway(model).embeddings(['first','second'])
        self.assertEqual(result[0][0],1)
        self.assertEqual(result[1][0],0)
        with self.assertRaises(ValueError): Gateway(lambda p,t:{'data':[]}).embeddings(['missing'])

    def test_load_harness_counts_failures(self):
        def operation(i):
            if i%4==0: raise TimeoutError()
        result=benchmark(operation,requests=40,workers=4)
        self.assertEqual(result['errors'],10); self.assertFalse(result['slo_pass'])

if __name__=='__main__': unittest.main()
