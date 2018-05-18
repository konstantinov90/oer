import json_patch
import asyncio
import json
import os

from aiohttp_auth import auth
import aiohttp.web
import aiohttp_cors
from pymongo import ReturnDocument

from db_api.api import db

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))

async def login(request):
    params = await request.json()
    username = params.get('username', None)
    user = await db.users.find_one({'_id': username})

    if not user:
        return aiohttp.web.HTTPForbidden(text='username')

    if params.get('password', None) == user['password']:
        await auth.remember(request, username)
        return aiohttp.web.Response(text=username)
    
    return aiohttp.web.HTTPForbidden(text='password')


def handle_socket_payload(payload):
    ans = dict(
        type='error',
        msg=f'''servers knows nothing of "{payload['type']}" message type!''',
    )
    if payload['type'] == 'hello':
        ans = dict(
            type='answer',
            msg='hello/answer',
        )

    return json.dumps(ans)

@auth.auth_required
async def test_auth(request):
    user = await auth.get_auth(request)
    print(user, 'logged in')
    return aiohttp.web.Response(text=user)


# @auth.auth_required
async def websocket_handler(request):
    print('Websocket connection starting')
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    print('Websocket connection ready')
    # cur_state = await db.current_state.find_one({'_id': 1}, {'_id': False})
    # await ws.send_json({'type': 'common/initState', 'msg': cur_state})

    ws_clients = request.app['ws_clients']

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            payload = json.loads(msg.data)
            print(payload)
            if payload['type'] == 'close':
                print('close')
                await ws.close()
            elif payload['type'] == 'auth':
                username = payload['msg']
                ws['user'] = username
                if ws_clients[username]:
                    await ws_clients[username].send_json({'type': 'common/unauthorize'})
                    await ws_clients[username].close()
                ws_clients[username] = ws
                await ws_clients.send_to_admin({'type': 'admin/clients', 'msg': ws_clients.get_users()})

                rio_entry = await db.rio.find_one({'_id': username})
                ws['rio_entry'] = rio_entry
                await ws.send_json({'type': 'common/rioEntry', 'msg': rio_entry})

                if username != 'admin':
                    possible_contragents = await db.rio.find({
                        'country_code': {'$ne': rio_entry['country_code']},
                        'dir': {'$ne': rio_entry['dir']}}
                    ).to_list(None)
                    await ws.send_json({'type': 'client/possibleContragents', 'msg': possible_contragents})

                await ws.send_json({'type': 'hasNewSessions'})

            elif 'user' not in ws:
                continue
            # elif payload['type'] == 'common/phase':
            #     await db.current_state.update_one({'_id': 1}, {'$set': {'phase': payload['msg']}}, upsert=True)
            # elif payload['type'] == 'bid':
            #     print(ws['user'])
            #     try:
            #         new_bid = json.loads(payload['msg'])
            #     except json.decoder.JSONDecodeError:
            #         continue
            #     if ws['user'] and ws['user'] != 'admin':
            #         new_bid['_id'] = ws['user']
            #     try:
            #         await db.bids.replace_one({'_id': new_bid['_id']}, new_bid, upsert=True)
            #     except Exception as e:
            #         print(e)
            #         pass
            #     await ws.send_json({'type': 'common/bid', 'msg': new_bid})
            #     if ws['user'] == 'admin' and new_bid['_id'] in ws_clients and ws_clients[new_bid['_id']]:
            #         await ws_clients[new_bid['_id']].send_json({'type': 'common/bid', 'msg': new_bid})
            #     elif ws['user'] == request.app['admin_subscribed_bid']:
            #         await ws_clients.send_to_admin({'type': 'common/bid', 'msg': new_bid})

            elif payload['type'] == 'queryBid':
                bid = await db.bids.find_one({
                    'trader_code': payload['msg']['username'],
                    'session_id': payload['msg']['session_id']
                })
                if username == 'admin':
                    await ws.send_json({'type': 'common/rioEntry', 'msg': await db.rio.find_one({'_id': payload['msg']['username']})})
                await ws.send_json({'type': 'common/bid', 'msg': bid })

            # elif payload['type'] == 'queryBidAdmin':
            #     username = payload['msg']
            #     request.app['admin_subscribed_bid'] = username
            #     bid = await db.bids.find_one({'_id': username})
            #     await ws.send_json({'type': 'common/rioEntry', 'msg': (await db.rio.find_one({'_id': username}))})
            #     await ws.send_json({'type': 'common/bid', 'msg': bid })

            # elif payload['type'] == 'common/date':
            #     cur_date = (await db.current_state.find_one({'_id': 1}))['date']
            #     await db.bids_arch.update_one({'date': cur_date}, {'$set': {'bids': (await db.bids.find().to_list(None))}}, upsert=True)
            #     await db.current_state.update_one({'_id': 1}, {'$set': {'date': payload['msg']}}, upsert=True)
            #     await db.bids.delete_many({})
            #     cur_bids = await db.bids_arch.find_one({'date': payload['msg']})
            #     if cur_bids and cur_bids['bids']:
            #         await db.bids.insert_many(cur_bids['bids'])

            elif payload['type'] == 'saveBid':
                _id = payload['msg'].get('_id')
                if _id:
                    await db.bids.find_one_and_replace({'_id': _id}, payload['msg'], upsert=True)
                else:
                    await db.bids.insert_one(payload['msg'])
                msg = {'type': 'hasNewBid'}
                await ws.send_json(msg)
                await ws_clients.send_to_admin(msg)

            elif payload['type'] == 'removeBid':
                _id = payload['msg']
                await db.bids.delete_many({'_id': _id})
                msg = {'type': 'hasNewBid'}
                await ws.send_json(msg)
                await ws_clients.send_to_admin(msg)


            elif payload['type'] == 'sdd':
                _id = payload['msg'].get('_id')
                if _id:
                    await db.sdd.find_one_and_replace({'_id': _id}, payload['msg'], upsert=True)
                else:
                    seq = await db.counters.find_one_and_update({'_id': 'sdd'},{'$inc': {'sequence_value': 1}}, return_document=ReturnDocument.AFTER)
                    payload['msg']['_id'] = seq['sequence_value']
                    await db.sdd.insert_one(payload['msg'])
                msg = {'type': 'hasNewSdd'}
                buyer = payload['msg']['buyer']
                seller = payload['msg']['seller']

                if ws_clients[buyer]:
                    await ws_clients[buyer].send_json(msg)
                if ws_clients[seller]:
                    await ws_clients[seller].send_json(msg)
                await ws_clients.send_to_admin(msg)

            elif payload['type'] == 'querySdd':
                username = ws['user']
                session = await db.sessions.find_one({'_id': payload['msg']})
                # sub_query = [{
                #     'dateStart': {'$lte': session['targetDate']},
                #     'dateEnd': {'$gte': session['targetDate']},
                # },
                # {
                #     'sessionId': session['_id'],
                # }]
                query = {
                    # 'sessionId': session['_id'],
                }

                if username != 'admin':
                    direction = 'buyer' if ws['rio_entry']['dir'] == 'buy' else 'seller'
                    query['$or'] = [
                        {
                            'author': username,
                            # '$or': sub_query,
                        },
                        {
                            direction: username,
                            '$and': [
                                {'status': {'$ne': 'rejected'}},
                                {'status': {'$ne': 'created'}},
                            ],
                            # '$or': sub_query,
                        }
                    ]

                    sdd = await db.sdd.find(query).to_list(None)
                    await ws_clients[username].send_json({'type': 'common/sdd', 'msg': sdd})
                else:
                    sdd = await db.sdd.find(query).to_list(None)
                    await ws_clients.send_to_admin({'type': 'common/sdd', 'msg': sdd})

            elif payload['type'] == 'openSession':
                seq = await db.counters.find_one_and_update({'_id': 'session'},{'$inc': {'sequence_value': 1}}, return_document=ReturnDocument.AFTER)
                payload['msg']['_id'] = seq['sequence_value']
                await db.sessions.insert_one(payload['msg'])
                await ws_clients.broadcast({'type': 'hasNewSessions'})

            elif payload['type'] == 'querySessions':
                sessions = await db.sessions.find().sort([('openDate', -1)]).to_list(None)
                await ws.send_json({'type': 'common/sessions', 'msg': sessions})

            
            
            if 'addressee' in payload:
                if payload['addressee'] == 'broadcast':
                    await ws_clients.broadcast(payload)
                elif ws_clients[payload['addressee']]:
                    await ws_clients[payload['addressee']].send_json(payload)

    print('Websocket connection closed')
    if 'user' in ws and ws_clients[ws['user']] == ws:
        ws_clients[ws['user']] = None
        print('user', ws['user'], 'deleted')
        await ws_clients.send_to_admin({'type': 'admin/clients', 'msg': ws_clients.get_users()})
    return ws

async def process_response(self, request, response):
    COOKIE_AUTH_KEY = 'aiohttp_auth.auth.CookieTktAuthentication'
    await super(auth.cookie_ticket_auth.CookieTktAuthentication, self).process_response(request, response)
    if COOKIE_AUTH_KEY in request:
        if hasattr(response, 'started') and response.started:
            raise RuntimeError("Cannot save cookie into started response")

        cookie = request[COOKIE_AUTH_KEY]
        if cookie == '':
            response.del_cookie(self.cookie_name)
        else:
            response.set_cookie(self.cookie_name, cookie)

auth.cookie_ticket_auth.CookieTktAuthentication.process_response = process_response


class WS_Clients(object):
    def __init__(self):
        self.clients = {}

    def __setitem__(self, key, item):
        self.clients[key] = item

    def __getitem__(self, key):
        return self.clients[key]

    def get_users(self):
        return {user: bool(ws) for user, ws in self.clients.items() if user != 'admin'}

    async def init(self):
        async for u in db.users.find({}, {'_id': 1}):
            self.clients[u['_id']] = None

    async def shutdown(self):
        for ws in list(self.clients.values()):
            if ws:
                await ws.close()
    
    async def broadcast(self, msg):
        for ws in self.clients.values():
            if ws:
                await ws.send_json(msg)

    async def send_to_admin(self, msg):
        if self.clients['admin']:
            await self.clients['admin'].send_json(msg)


async def shutdown_websockets(app):
    await app['ws_clients'].shutdown()

async def prepare_ws_clients(app):
    clients = WS_Clients()
    await clients.init()
    app['ws_clients'] = clients

@aiohttp.web.middleware
async def index(request, handler):
    try:
        return await handler(request)
    except aiohttp.web.HTTPException as err:
        if err.status == 404:
            return aiohttp.web.FileResponse('../client/dist/index.html')
        raise

def main():
    loop = asyncio.get_event_loop()

    policy = auth.CookieTktAuthentication(os.urandom(32), 60000,
                                          include_ip=True)

    middlewares = [auth.auth_middleware(policy)]
    if os.environ['NODE_ENV'] == 'production':
        middlewares.append(index)
    app = aiohttp.web.Application(loop=loop, middlewares=middlewares)
    
    # print(loop.run_until_complete(db.users.find({}, {'_id': 1})))
    # app['ws_clients'] = {r['_id']: None for r in loop.run_until_complete(db.users.find({}, {'_id': 1}))}
    app['admin_subscribed_bid'] = ''
    app.on_startup.append(prepare_ws_clients)
    app.on_shutdown.append(shutdown_websockets)

    # app.router.add_route('GET', '/', testhandle)

    r1 = app.router.add_route('GET', '/test_auth/', test_auth)

    r2 = app.router.add_route('POST', '/login/', login)

    r3 = app.router.add_route('GET', '/ws', websocket_handler)
    
    if os.environ['NODE_ENV'] == 'production':
        app.router.add_static('/', '../client/dist')
    else:
        cors = aiohttp_cors.setup(app, defaults={
            '*': aiohttp_cors.ResourceOptions(
                    expose_headers='*',
                    allow_headers='*',
                    allow_credentials=True),
        })

        cors.add(r1)
        cors.add(r2)
        cors.add(r3)

    aiohttp.web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
