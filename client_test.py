from client import client

with open('token.txt') as fp:
    tokens = fp.read().split('\n')

async def main():
    async with client(
        token = tokens[0],
        refresh_token = tokens[1]
    ) as c:
        async with c.conversation() as conv:
            print(await conv.prompt('测试信息'))

if __name__ == '__main__':
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())