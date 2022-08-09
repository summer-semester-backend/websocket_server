import json
# from user.models import User

# from django.shortcuts import render
import threading
import websockets
import websockets.exceptions
import asyncio
import time, traceback

FILES = {}


def broadcast_thread():
    print("?????????????????????????")
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # start_server = websockets.serve(unknown, '127.0.0.1', 8001)
    # asyncio.get_event_loop().run_until_complete(start_server)
    # asyncio.get_event_loop().run_forever()
    start_server = websockets.serve(unknown, "0.0.0.0", 8001)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


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
                    except websockets.exceptions.ConnectionClosed:
                        print(e)
    except Exception as e:
        print(e)
        # traceback.print_exc(e)
    if userID != -1 and fileID != -1:
        leave(userID, fileID) # 连接关闭时自动向所有编辑同一文件的用户发送leave消息


broadcast_thread()
