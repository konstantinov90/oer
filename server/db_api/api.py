from motor import motor_asyncio as motor

client = motor.AsyncIOMotorClient('localhost', 27017)

db = client['inter_market']
