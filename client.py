import aiohttp
import json
from conversation import conversation

class client:
    def __init__(self, token, refresh_token):
        self.token = token
        self.refresh_token = refresh_token
        self.session = aiohttp.ClientSession()
    
    async def _post(self, url, content) -> dict:
        async with self.session.post(f'https://chatglm.cn{url}', headers = {
            'Authorization': f"Bearer {self.token}",
            "Content-Type": "application/json;charset=UTF-8",
            'Origin': 'https://chatglm.cn',
            'Referer': 'https://chatglm.cn/detail',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
            'Cookie': f'chatglm_token={self.token}; chatglm_refresh_token={self.refresh_token}'
        }, data = json.dumps(content)) as r:
            return await r.json()
    
    async def _get(self, url) -> dict:
        async with self.session.get(f'https://chatglm.cn{url}', headers = {
            'Authorization': f"Bearer {self.token}",
            'Origin': 'https://chatglm.cn',
            'Referer': 'https://chatglm.cn/detail',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
            'Cookie': f'chatglm_token={self.token}; chatglm_refresh_token={self.refresh_token}'
        }) as r:
            return await r.json()
    
    async def _get_event_stream(self, url):
        async with self.session.get(f'https://chatglm.cn{url}', headers = {
            'Authorization': f"Bearer {self.token}",
            'Accept': 'text/event-stream',
            'Origin': 'https://chatglm.cn',
            'Referer': 'https://chatglm.cn/detail',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
            'Cookie': f'chatglm_token={self.token}; chatglm_refresh_token={self.refresh_token}'
        }) as r:
            return client._resolve_event_stream(await r.text())
    
    async def request_create_conversation(self, prompt) -> str:
        return (await self._post('/chatglm/backend-api/v1/conversation', {
            "prompt": prompt
        }))["result"]["task_id"]
    
    @staticmethod
    def _resolve_event_stream(text: str):
        evt = None
        data = []
        id = None

        for line in text.split('\n'):
            if line.startswith('id:'):
                id = line[3:]
            elif line.startswith('event:'):
                evt = line[6:]
            elif line.startswith('data:'):
                data.append(line[5:])
            elif line == '':
                if evt == 'add':
                    yield (evt, data, id)
                evt = None
                data.clear()
    
    async def request_stream_context(self, conversation_task_id, prompt, seed):
        resp = await self._post(f'/chatglm/backend-api/v1/stream_context', {
            "conversation_task_id": conversation_task_id,
            'max_tokens': 512,
            'prompt': prompt,
            'seed': seed,
            'retry': False,
            'retry_history_task_id': None
        })

        res = None
        for (evt, data, _) in await self._get_event_stream(f'/chatglm/backend-api/v1/stream?context_id={resp["result"]["context_id"]}'):
            if evt == 'add' and data: res = data[0]
        
        return res

    async def request_delete_conversation(self, conversation_task_id):
        return await self._get(f'/chatglm/backend-api/v1/conversation/delete/{conversation_task_id}')
    
    def conversation(self):
        return conversation(self)

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()