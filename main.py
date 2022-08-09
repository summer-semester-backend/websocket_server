import json
# from user.models import User

# from django.shortcuts import render
import threading
from datetime import datetime

import websockets
import websockets.exceptions
import asyncio
import time, traceback

FILES = {}


async def broadcast_thread():
    print("?????????????????????????")
    heartbeat_task = heartbeat()
    asyncio.create_task(heartbeat_task)
    async with websockets.serve(unknown, "0.0.0.0", 8001):
        await asyncio.Future()
    # asyncio.create_task(start_server)
    # asyncio.get_event_loop().run_until_complete(start_server)
    # asyncio.get_event_loop().run_forever()
    await heartbeat_task
    # await start_server


def leave(userID, fileID):
    print('用户{}连接已断开'.format(userID))
    data = {
        'operation': 'leave',
        'userID': userID,
        'fileID': fileID,
    }
    message = json.dumps(data)
    FILES[fileID].pop(userID)
    connections = set(FILES[fileID].values())
    websockets.broadcast(connections, message)


async def unknown(websocket):
    await websocket.send(json.dumps({'result': 0, 'message': '正在连接...'}))
    userID = -1
    fileID = -1
    try:
        async for message in websocket:
            # if 
            print("接收到: "+message)
            data = json.loads(message)
            if data['operation'] == 'register':  # 连接
                await websocket.send(json.dumps({'result': 0, 'message': '已连接到同步编辑服务'}))
                fileID = data['fileID']
                userID = data['userID']
                if fileID not in FILES:
                    FILES[fileID] = {}
                for theirID in FILES[fileID]: # 将此前存在的用户告知新用户
                    await websocket.send(json.dumps({
                        'operation': 'register',
                        'userID': theirID,
                        'fileID': fileID,
                    }))
                FILES[fileID][userID] = websocket
            elif data['operation'] == 'leave':  # 断开连接
                leave(userID, fileID)
            data['timestamp'] = str(time.time())
            message = json.dumps(data)
            dic = FILES[fileID]
            for that_userID in dic:
                if that_userID != userID:
                    try:
                        await dic[that_userID].send(message)
                    except websockets.exceptions.ConnectionClosed as e:
                        print(e)
    except Exception as e:
        print(e)
        # traceback.print_exc(e)
    if userID != -1 and fileID != -1:
        leave(userID, fileID) # 连接关闭时自动向所有编辑同一文件的用户发送leave消息


async def heartbeat():
    while True:
        ws_set = set()
        for file in FILES.values():
            for ws in file.values():
                ws_set.add(ws)
        message = json.dumps({'operation': 'heartbeat', 'timestamp': str(time.time())})
        websockets.broadcast(ws_set, message)
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("{}: 时间戳已广播到{}个客户端".format(t, len(ws_set)))
        await asyncio.sleep(10)


asyncio.run(broadcast_thread())
# await heartbeat_task
