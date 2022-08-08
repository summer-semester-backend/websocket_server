import json
# from user.models import User

# from django.shortcuts import render
import threading
import websockets
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


async def unknown(websocket):
    await websocket.send(json.dumps({'result': 0, 'message': '正在连接...'}))
    async for message in websocket:
        print("接收到: "+message)
        data = json.loads(message)
        # print(data)
        if data['operation'] == 'register':  # 连接
            await websocket.send(json.dumps({'result': 0, 'message': '已连接到同步编辑服务'}))
            fileID = data['fileID']
            userID = data['userID']
            if fileID not in FILES:
                FILES[fileID] = {}
            dic = FILES[fileID]
            for that_userID in dic:
                await websocket.send(json.dumps({
                    'operation': 'register',
                    'userID': that_userID,
                    'fileID': fileID,
                }))
            # broad = {'result': 0, 'message': '用户' + str(userID) + "已加入编辑"}
            FILES[fileID][userID] = websocket
        elif data['operation'] == 'leave':  # 断开连接
            # websocket.send(json.dumps({'result': 0, 'message': '已连接到同步编辑服务'}))
            fileID = data['fileID']
            userID = data['userID']
            dic = FILES[fileID]
            broad = {'result': 0, 'message': '用户' + str(userID) + "已离开"}
            FILES[fileID].pop(userID)
        data['timestamp'] = str(time.time())
        message = json.dumps(data)
        dic = FILES[data['fileID']]
        for that_userID in dic:
            if that_userID != data['userID']:
                # if dic[that_userID]
                try:
                    await dic[that_userID].send(message)
                except:
                    del dic[that_userID]
        # if len(dic.values()) > 0:
        #     print("向{}个用户发起转发".format(len(dic.values())))
        #     await asyncio.wait([ws.send(message) for ws in dic.values()])

broadcast_thread()
