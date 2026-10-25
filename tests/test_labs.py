import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from qwenlabs.client import Qwen
from qwenlabs.core import chunks, retrieve, validate_ticket, execute_tool, retry, percentile
from qwenlabs.run import run

class Labs(unittest.TestCase):
    def test_all_offline_labs_never_send_requests(self):
        with patch('qwenlabs.client.urlopen',side_effect=AssertionError('Network forbidden')):
            for lab in range(1,10):
                with self.subTest(lab=lab):
                    self.assertIsInstance(run(lab),dict)
    def test_chunk_boundaries(self):
        self.assertEqual(chunks('a b c d e',3,1),['a b c','c d e'])
        self.assertEqual(chunks(''),[])
        with self.assertRaises(ValueError): chunks('x',2,2)
    def test_retrieval_abstains(self):
        self.assertEqual(retrieve('xyzzynotaword'),[])
        self.assertEqual(retrieve('objects buckets',k=1)[0]['id'],'oss')
    def test_schema_rejects_invalid_or_extra_fields(self):
        for text in ('[]','{"category":"billing","priority":"urgent"}','{"category":"billing","priority":"low","execute":"rm"}'):
            with self.assertRaises(ValueError): validate_ticket(text)
    def test_tool_rejects_arbitrary_execution(self):
        for name,args in [('shell',{'service':'oss'}),('lookup_service',{'service':'../../etc/passwd'}),('lookup_service',{'service':'oss','command':'ls'})]:
            with self.assertRaises(ValueError): execute_tool(name,args)
    def test_retry_auth_fails_fast(self):
        errors=[]
        def fail():
            errors.append(1)
            raise HTTPError('https://example.com',401,'unauthorized',{},None)
        with self.assertRaises(HTTPError): retry(fail,sleep=lambda _:None)
        self.assertEqual(len(errors),1)
    def test_retry_exhaustion(self):
        calls=[]
        def fail():
            calls.append(1)
            raise TimeoutError()
        with self.assertRaises(TimeoutError): retry(fail,sleep=lambda _:None)
        self.assertEqual(len(calls),3)
    def test_cloud_payload_and_timeout(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self,*_): pass
            def read(self): return b'{"choices":[{"message":{"content":"ready"}}]}'
        with patch.dict('os.environ',{'DASHSCOPE_API_KEY':'fixture','DASHSCOPE_BASE_URL':'https://workspace.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1'}):
            with patch('qwenlabs.client.urlopen',return_value=Response()) as send:
                self.assertEqual(Qwen(True).answer('hello'),'ready')
                request=send.call_args.args[0]
                self.assertEqual(json.loads(request.data)['max_tokens'],256)
                self.assertEqual(send.call_args.kwargs['timeout'],45)
    def test_configuration_required(self):
        with patch.dict('os.environ',{},clear=True):
            with self.assertRaises(ValueError): Qwen(True)
    def test_percentiles(self):
        self.assertEqual(percentile([5,1,3,2,4],.95),5)
        self.assertEqual(percentile([5,1,3,2,4],.5),3)
        with self.assertRaises(ValueError): percentile([],.95)

if __name__=='__main__': unittest.main()
