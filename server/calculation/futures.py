from datetime import datetime
import os.path
import uuid
from xml.etree import ElementTree as ET
import pymongo

from .model_file_loader import ModelFileLoader

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')

db = pymongo.MongoClient().inter_market

def make_registry(sd_session_id):

    root = ET.Element('message')
    root.attrib['class'] = 'SECTION_FLOW_LIMIT_EX'
    root.attrib['created-date'] = datetime.now().strftime('%Y%m%d%H%M%S')
    root.attrib['guid'] = str(uuid.uuid4())

    for sec_lim in db.section_limits.find({
            'limit_type': 'SECTION_FLOW_LIMIT_EX',
            'session_id': sd_session_id,
        }):
        for hour in sec_lim['hours']:
            for sec in hour['sections']:
                from_code, to_code = sec['section_code'].split('-')

                sub = ET.SubElement(root, 'row')
                sub.attrib['country-code-from'] = from_code
                sub.attrib['country-code-to'] = to_code
                sub.attrib['section-code'] = sec['section_code']
                sub.attrib['target-day'] = sec_lim['target_date'].strftime('%Y%m%d')
                sub.attrib['target-hour'] = str(hour['hour'])
                sub.attrib['flow-limit'] = str(sec['pmax_fw'])

                sub = ET.SubElement(root, 'row')
                sub.attrib['country-code-from'] = to_code
                sub.attrib['country-code-to'] = from_code
                sub.attrib['section-code'] = sec['section_code']
                sub.attrib['target-day'] = sec_lim['target_date'].strftime('%Y%m%d')
                sub.attrib['target-hour'] = str(hour['hour'])
                sub.attrib['flow-limit'] = str(sec['pmax_bw'])

    with open(os.path.join(BASE_PATH, 'Section_limits_EX.xml'), 'bw') as fd:
        fd.write(ET.tostring(root, encoding='utf-8', method='xml'))


def upload_registry(session_id):
    data = ModelFileLoader.parse_section_limits(os.path.join(BASE_PATH, 'Section_limits_DAM.xml'), 'SECTION_FLOW_LIMIT_DAM')
    for row in data:
        row.update(session_id=session_id)
    db.section_limits.insert_many(data)
