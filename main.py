import json
# from user.models import User

# from django.shortcuts import render
import threading
import websockets
import websockets.exceptions
import asyncio
import time

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


def leave(userID):
    print('用户{}连接已断开'.format(userID))
    data = {
        'operation': 'leave',
        'userID': userID,
        'fileID': 0,
    }
    for fileID in FILES:
        if userID in FILES[fileID]: # 用户参与了这个文件的编辑
            FILES[fileID].pop(userID)
            data['fileID'] = fileID
            connections = set(FILES[fileID].values())
            websockets.broadcast(connections, json.dumps(data))


async def unknown(websocket):
    await websocket.send(json.dumps({'result': 0, 'message': '正在连接...'}))
    myID = -1
    async for message in websocket:
        print("接收到: "+message)
        data = json.loads(message)
        fileID = data['fileID']
        userID = data['userID']
        myID = userID
        if data['operation'] == 'register':  # 连接
            await websocket.send(json.dumps({'result': 0, 'message': '已连接到同步编辑服务'}))
            if fileID not in FILES:
                FILES[fileID] = {}
            dic = FILES[fileID]
            FILES[fileID][userID] = websocket
        elif data['operation'] == 'leave':  # 断开连接
            leave(userID)
        data['timestamp'] = str(time.time())
        message = json.dumps(data)
        dic = FILES[data['fileID']]
        for that_userID in dic:
            if that_userID != data['userID']:
                await dic[that_userID].send(message)
                # except websockets.exceptions.ConnectionClosed:
                #     leave(that_userID)
        # if len(dic.values()) > 0:
        #     print("向{}个用户发起转发".format(len(dic.values())))
        #     await asyncio.wait([ws.send(message) for ws in dic.values()])
    leave(myID)


broadcast_thread()
