import json
# from user.models import User

# from django.shortcuts import render
import threading
import websockets
import asyncio

FILES = {}


def broadcast_thread():
    print("?????????????????????????")
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # start_server = websockets.serve(unknown, '127.0.0.1', 8001)
    # asyncio.get_event_loop().run_until_complete(start_server)
    # asyncio.get_event_loop().run_forever()
    start_server = websockets.serve(unknown, "127.0.0.1", 8001)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


async def unknown(websocket):
    await websocket.send({'result': 0, 'message': '正在连接...'})
    async for message in websocket:
        data = json.loads(message)
        print(data)
        if data['operation'] == 'register':  # 连接
            websocket.send(json.dumps({'result': 0, 'message': '已连接到同步编辑服务'}))
            fileID = data['fileID']
            userID = data['userID']
            if fileID not in FILES:
                FILES[fileID] = {}
            dic = FILES[fileID]
            broad = {'result': 0, 'message': '用户' + str(userID) + "已加入编辑"}
            await asyncio.wait([ws.send(json.dumps(broad)) for ws in dic.values()])
            FILES[data['fileID']][data['userID']] = websocket
        elif data['operation'] == 'change':
            pass
        elif data['operation'] == 'leave':  # 断开连接
            # websocket.send(json.dumps({'result': 0, 'message': '已连接到同步编辑服务'}))
            fileID = data['fileID']
            userID = data['userID']
            dic = FILES[fileID]
            broad = {'result': 0, 'message': '用户' + str(userID) + "已离开"}
            FILES[fileID].pop(userID)
            await asyncio.wait([ws.send(json.dumps(broad)) for ws in dic.values()])

broadcast_thread()
