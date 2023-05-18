import random

class conversation:
    def __init__(self, client: 'client'):
        self.client = client
        self.created = False
        self.id = None


    async def prompt(self, text):
        if not self.created:
            self.id = await self.client.request_create_conversation(text)
            self.created = True
        
        return await self.client.request_stream_context(self.id, text, random.randint(0, 100000))
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.created:
            await self.client.request_delete_conversation(self.id)
            self.created = False
            self.id = None