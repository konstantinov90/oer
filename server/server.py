import json_patch
import asyncio
import json
import os
import os.path
import re

from aiohttp_auth import auth
import aiohttp.web
import aiohttp_cors
from pymongo import ReturnDocument
from multidict import MultiDict

from calculation.spot import SpotModelAug
from calculation.sd import SdModelAug
from calculation import futures
from db_api.api import db
import reports

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))

BASE_PATH = os.path.dirname(__file__)

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

async def upload_file(request):
    session_id = int(request.rel_url.query['session_id'])
    reader = await request.multipart()

    field = await reader.next()
    assert field.name == 'file'
    filename = field.filename

    if re.match('^SECTION_FLOW_LIMIT.*', field.filename):
        func = futures.upload_section_limits
    elif re.match('^DEAL_EX.*', field.filename):
        func = futures.upload_contracts
    else:
        return aiohttp.web.HTTPNotFound()

    filename = os.path.join(BASE_PATH, field.filename)

    size = 0
    with open(filename, 'wb') as fd:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            fd.write(chunk)

    func(session_id, filename)
    
    return aiohttp.web.Response(text=filename)

async def bids(request):
    session_id = int(request.rel_url.query['session_id'])
    bids = await db.bids.find({'session_id': session_id}).to_list(None)
    return aiohttp.web.json_response(bids)

async def _download_file(request, filename, file_type='xlsx'):
    resp = aiohttp.web.StreamResponse(headers=MultiDict({
        'CONTENT-DISPOSITION': f'attachment; filename="{os.path.split(filename)[-1]}"',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if file_type == 'xlsx' else 'application/xml',
    }))

    resp.content_length = os.stat(filename).st_size
    await resp.prepare(request)

    with open(filename, 'rb') as fd:
        await resp.write(fd.read())

    return resp

async def bid_report(request):
    session_id, username = int(request.rel_url.query['session_id']), request.rel_url.query['username']

    if username == 'admin':
        return await _download_file(request, reports.report_admin_bid(session_id, username))
    return await _download_file(request, reports.report_user_bid(session_id, username))

async def sdd_report(request):
    session_id, username = int(request.rel_url.query['session_id']), request.rel_url.query['username']

    return await _download_file(request, reports.report_user_sdd(session_id, username))

async def sdd_section_limits(request):
    sd_session_id = int(request.rel_url.query['sd_session_id'])

    return await _download_file(request, futures.make_registry(sd_session_id), file_type='xml')


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
            # print(payload)
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

                rio_entry = await db.rio.find_one({'login': username})
                ws['rio_entry'] = rio_entry
                await ws.send_json({'type': 'common/rioEntry', 'msg': rio_entry})

                if username != 'admin':
                    possible_contragents = await db.rio.find({
                        'country_code': {'$ne': rio_entry['country_code']},
                        'dir': {'$ne': rio_entry['dir']}}
                    ).to_list(None)
                    await ws.send_json({'type': 'client/possibleContragents', 'msg': possible_contragents})
                else:
                    await ws.send_json({'type': 'client/possibleContragents', 'msg': (await db.rio.find().to_list(None))})

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
                if username == 'admin':
                    if not payload['msg']['username']:
                        continue
                    rio_entry = await db.rio.find_one({'login': payload['msg']['username']})
                    await ws.send_json({'type': 'common/rioEntry', 'msg': rio_entry})
                    bid = await db.bids.find_one({
                        'trader_code': rio_entry['_id'],
                        'session_id': payload['msg']['session_id']
                    })
                else:
                    bid = await db.bids.find_one({
                        'trader_code': payload['msg']['username'],
                        'session_id': payload['msg']['session_id']
                    })
                await ws.send_json({'type': 'common/bid', 'msg': bid })

            elif payload['type'] == 'queryAllBids':
                session = await db.sessions.find_one({'_id': payload['msg']})
                if session['status'] != 'closed':
                    continue
                bids = await db.bids.find({'session_id': payload['msg']}).to_list(None)
                await ws.send_json({'type': 'common/allBids', 'msg': bids})

            elif payload['type'] == 'querySpotResults':
                session = await db.sessions.find_one({'_id': payload['msg']})
                results = await db.spot_results.find_one({'session_id': session['_id']})
                await ws.send_json({'type': 'common/spotResults', 'msg': results})

            elif payload['type'] == 'calculate':
                session = await db.sessions.find_one({'_id': payload['msg']})
                await db.sessions.find_one_and_update({'_id': payload['msg']}, {'$set': {'status': 'calculation'}})
                if session['type'] == 'free':
                    await db.sdd.delete_many({'sessionId': session['_id'], 'status': {'$ne': 'registered'}})
                    SdModelAug.sd_runner(session['_id'])
                    await db.sessions.find_one_and_update({'_id': payload['msg']}, {'$set': {'status': 'closed'}})
                    await ws_clients.broadcast({'type': 'hasNewSdd'})
                elif session['type'] == 'spot':
                    SpotModelAug.spot_runner(session['_id'], session['futures_session_id'])
                    await db.sessions.find_one_and_update({'_id': payload['msg']}, {'$set': {'status': 'closed'}})
                    await ws_clients.broadcast({'type': 'hasNewBid'})

                await ws_clients.broadcast({'type': 'hasNewSessions'})
            elif payload['type'] == 'querySectionLimits':
                session_id, target_date, limit_type = payload['sessionId'], payload['targetDate'], payload['limitType']
                session = await db.sessions.find_one({'_id': session_id})
                if limit_type == 'SECTION_FLOW_LIMIT_FC' and session['type'] == 'free':
                    session_id = {'$exists': False}
                elif limit_type == 'SECTION_FLOW_LIMIT_EX_mod' and session['type'] == 'futures':
                    session_id = session['sd_session_id']
                elif limit_type == 'SECTION_FLOW_LIMIT_DAM_mod' and session['type'] == 'spot':
                    session_id = session['futures_session_id']

                section_limits = await db.section_limits.find_one({
                    'session_id': session_id,
                    'target_date': target_date,
                    'limit_type': limit_type,
                })
                await ws.send_json({'type': 'common/sectionLimits', 'msg': section_limits})

            elif payload['type'] == 'queryContractsSumVolume':
                if ws['user'] == 'admin':
                    if not payload['username']:
                        continue
                    rio_entry = await db.rio.find_one({'login': payload['username']})
                else:
                    rio_entry = ws['rio_entry']
                session = await db.sessions.find_one({'_id': payload['sessionId']})
                if session['type'] == 'spot':
                    futures_session = await db.sessions.find_one({'_id': session['futures_session_id']})
                    sd_session = await db.sessions.find_one({'_id': futures_session['sd_session_id']})
                    if rio_entry['dir'] == 'buy':
                        query = {'buyer': rio_entry['_id']}
                    else:
                        query = {'seller': rio_entry['_id']}
                    sum_contracts = []
                    async for doc in db.sdd.aggregate([
                        {'$match': query},
                        {'$unwind': '$values'},
                        {'$match': {'values.tdate': session['startDate']}},
                        {'$group': {'_id': '$values.hour', 'vol': {'$sum': '$values.accepted_volume'}}}
                    ]):
                        sum_contracts.append(doc)
                    await ws.send_json({'type': 'common/contractsSumVolume', 'msg': sum_contracts})

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
                session = await db.sessions.find_one({'_id': payload['msg']['sessionId']})
                if session['status'] != 'open':
                    await ws.send_json({'type': 'hasNewSessions'})
                    continue
                if _id:
                    await db.sdd.find_one_and_replace({'_id': _id}, payload['msg'], upsert=True)
                else:
                    seq = await db.counters.find_one_and_update({'_id': 'sdd'},{'$inc': {'sequence_value': 1}}, return_document=ReturnDocument.AFTER)
                    payload['msg']['_id'] = seq['sequence_value']
                    await db.sdd.insert_one(payload['msg'])
                msg = {'type': 'hasNewSdd'}
                buyer = (await db.rio.find_one({'_id': payload['msg']['buyer']}))['_id']
                seller = (await db.rio.find_one({'_id': payload['msg']['seller']}))['_id']

                if ws_clients[buyer]:
                    await ws_clients[buyer].send_json(msg)
                if ws_clients[seller]:
                    await ws_clients[seller].send_json(msg)
                await ws_clients.send_to_admin(msg)
                # await ws_clients.broadcast(msg)

            elif payload['type'] == 'deleteSdd':
                await db.sdd.delete_many({'_id': payload['msg']})
                msg = {'type': 'hasNewSdd'}
                await ws.send_json(msg)
                await ws_clients.send_to_admin(msg)

            elif payload['type'] == 'querySdd':
                session = await db.sessions.find_one({'_id': payload['msg']})
                # sub_query = [{
                #     'dateStart': {'$lte': session['targetDate']},
                #     'dateEnd': {'$gte': session['targetDate']},
                # },
                # {
                #     'sessionId': session['_id'],
                # }]
                query = {
                    '$and': [
                        {
                            '$or': [
                                {
                                    'sessionId': session['_id'],
                                },
                                {
                                    'dateEnd': {'$gte': session['startDate']}
                                },
                            ],
                        },
                        {},
                    ]
                }

                if ws['user'] != 'admin':
                    direction = 'buyer' if ws['rio_entry']['dir'] == 'buy' else 'seller'
                    query['$and'][1]['$or'] = [
                        {
                            'author': ws['rio_entry']['_id'],
                            # '$or': sub_query,
                        },
                        {
                            direction: ws['rio_entry']['_id'],
                            '$and': [
                                {'status': {'$ne': 'rejected'}},
                                {'status': {'$ne': 'created'}},
                            ],
                            # '$or': sub_query,
                        }
                    ]

                    sdd = await db.sdd.find(query).to_list(None)
                    await ws.send_json({'type': 'common/sdd', 'msg': sdd})
                else:
                    sdd = await db.sdd.find(query).to_list(None)
                    await ws_clients.send_to_admin({'type': 'common/sdd', 'msg': sdd})

            elif payload['type'] == 'queryAllSdd':
                rio = await db.rio.find().to_list(None)
                session = await db.sessions.find_one({'_id': payload['msg']})
                # if session['status'] != 'closed' and ws['user'] != 'admin':
                #     continue
                sdd = await db.sdd.find({'sessionId': payload['msg'], 'status': 'registered'}).to_list(None)
                for sd in sdd:
                    sd['buyer'] = [row for row in rio if row['_id'] == sd['buyer']][0]
                    sd['seller'] = [row for row in rio if row['_id'] == sd['seller']][0]
                await ws.send_json({'type': 'common/allSdd', 'msg': sdd})

            elif payload['type'] == 'openSession':
                seq = await db.counters.find_one_and_update({'_id': 'session'},{'$inc': {'sequence_value': 1}}, return_document=ReturnDocument.AFTER)
                payload['msg']['_id'] = seq['sequence_value']
                await db.sessions.insert_one(payload['msg'])
                await ws_clients.broadcast({'type': 'hasNewSessions'})
            elif payload['type'] == 'querySessions':
                sessions = await db.sessions.find().sort([('openDate', -1)]).to_list(None)
                await ws.send_json({'type': 'common/sessions', 'msg': sessions})
                await ws_clients.broadcast({'type': 'hasNewResults'})

            elif payload['type'] == 'futuresCloseSession':
                await db.sessions.find_one_and_update({'_id': payload['msg']}, {'$set': {'status': 'closed'}})
                await ws_clients.broadcast({'type': 'hasNewSessions'})

            elif payload['type'] == 'queryAllFutures':
                futures = await db.futures.find({'session_id': payload['msg']}).to_list(None)
                calendar = await db.calendar.find().to_list(None)
                await ws.send_json({'type': 'common/calendar', 'msg': calendar})
                await ws.send_json({'type': 'common/allFutures', 'msg': futures})
            
            elif payload['type'] == 'queryMgp':
                mgp = await db.mgp_prices.find_one({
                    'period_type': 'D',
                    'graph_type': 'FR',
                    'date_from': payload['msg'],
                    'date_to': payload['msg'],
                })
                await ws.send_json({'type': 'common/mgp', 'msg': mgp})

            elif payload['type'] == 'reopen':
                session = await db.sessions.find_one({'_id': payload['msg']})
                if session['type'] == 'spot':
                    rio = {row['_id']: row for row in await db.rio.find({}).to_list(None)}
                    for bid in await db.bids.find({'session_id': payload['msg']}).to_list(None):
                        rio_entry = rio[bid['trader_code']]
                        for hour in bid['hours']:
                            hour['intervals'][0]['prices'] = [row for row in hour['intervals'][0]['prices'] if row['section_code'] in rio_entry['section_codes']]
                        await db.bids.find_one_and_replace({'_id': bid['_id']}, bid)
                    await db.spot_results.delete_many({'session_id': payload['msg']})
                    await db.sessions.update_one({'_id': payload['msg']}, {'$set': {'status': 'open'}})
                    await ws_clients.broadcast({'type': 'hasNewSessions'})
                    await ws_clients.broadcast({'type': 'hasNewBid'})
            
            
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

async def index(request):
    return aiohttp.web.FileResponse('../client/dist/index.html')

@aiohttp.web.middleware
async def index_middleware(request, handler):
    try:
        return await handler(request)
    except aiohttp.web.HTTPException as err:
        if err.status == 404:
            return await index(request)
        raise

async def indx(req):
    return aiohttp.web.Response(text='bye')

def main():
    loop = asyncio.get_event_loop()

    policy = auth.CookieTktAuthentication(os.urandom(32), 60000,
                                          include_ip=True)

    middlewares = [auth.auth_middleware(policy)]
    if os.environ['NODE_ENV'] == 'production':
        middlewares.append(index_middleware)
    app = aiohttp.web.Application(loop=loop, middlewares=middlewares)
    
    # print(loop.run_until_complete(db.users.find({}, {'_id': 1})))
    # app['ws_clients'] = {r['_id']: None for r in loop.run_until_complete(db.users.find({}, {'_id': 1}))}
    app['admin_subscribed_bid'] = ''
    app.on_startup.append(prepare_ws_clients)
    app.on_shutdown.append(shutdown_websockets)

    app.router.add_get('/index/', indx)

    r1 = app.router.add_route('GET', '/test_auth/', test_auth)

    r2 = app.router.add_route('POST', '/login/', login)

    r3 = app.router.add_route('GET', '/ws', websocket_handler)

    app.router.add_get('/rest/bids/', bids)
    r4 = app.router.add_get('/rest/bid_report/', bid_report)
    r5 = app.router.add_get('/rest/sdd_report/', sdd_report)
    r6 = app.router.add_get('/rest/sdd_section_limits/', sdd_section_limits)
    r7 = app.router.add_post('/rest/upload_file/', upload_file)
    
    if os.environ['NODE_ENV'] == 'production':
        app.router.add_route('GET', '/', index)
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
        cors.add(r4)
        cors.add(r5)
        cors.add(r6)
        cors.add(r7)

    aiohttp.web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
