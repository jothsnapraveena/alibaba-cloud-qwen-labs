"""Explicit live mode, bounded output, no third-party dependencies."""
import json
import os
from urllib.request import Request, urlopen
from urllib.parse import urlparse

class Qwen:
    def __init__(self, live=False):
        self.live = live
        self.model = os.getenv('QWEN_MODEL', 'qwen-plus')
        self.base = os.getenv('DASHSCOPE_BASE_URL', '')
        self.key = os.getenv('DASHSCOPE_API_KEY', '')
        if live:
            host = urlparse(self.base).hostname or ''
            if not self.key or not self.base.startswith('https://') or not host.endswith('.aliyuncs.com'):
                raise ValueError('Set a Model Studio HTTPS DASHSCOPE_BASE_URL and DASHSCOPE_API_KEY')
            if '{' in self.base:
                raise ValueError('Replace the workspace placeholder in DASHSCOPE_BASE_URL')

    def chat(self, messages, **options):
        if not self.live:
            raise RuntimeError('Offline exercises must not call the cloud')
        payload = {'model': self.model, 'messages': messages, 'max_tokens': 256, **options}
        req = Request(self.base.rstrip('/')+'/chat/completions',
                      data=json.dumps(payload).encode(),
                      headers={'Authorization': 'Bearer '+self.key, 'Content-Type': 'application/json'})
        with urlopen(req, timeout=45) as response:
            return json.load(response)

    def answer(self, prompt, system='You are a concise technical assistant.'):
        result = self.chat([{'role':'system','content':system}, {'role':'user','content':prompt}])
        return result['choices'][0]['message']['content']
