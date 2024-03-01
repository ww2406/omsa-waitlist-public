import math

import requests, re
from typing import TypedDict, List
import firebase_admin
from firebase_admin import firestore, messaging
import os


class ClassRec(TypedDict):
    title: str
    crn: int
    term: str
    dept_course_nbr: str
    seat_capacity: int
    seat_actual: int
    seat_remaining: int
    wl_capacity: int
    wl_actual: int
    wl_remaining: int
    subscribers: list


def get_classes(subj: str, term: str) -> List[ClassRec]:
    url = "https://oscar.gatech.edu/bprod/bwckschd.p_get_crse_unsec"

    payload = {'term_in': term,
               'sel_subj': ['dummy', subj],
               'sel_day': 'dummy',
               'sel_schd': ['dummy', '%'],
               'sel_insm': 'dummy',
               'sel_camp': ['dummy', 'O'],
               'sel_levl': 'dummy',
               'sel_sess': 'dummy',
               'sel_instr': ['dummy', '%'],
               'sel_ptrm': ['dummy', '%'],
               'sel_attr': ['dummy', '%'],
               'sel_crse': '',
               'sel_title': '',
               'sel_from_cred': '',
               'sel_to_cred': '',
               'begin_hh': '0',
               'begin_mi': '0',
               'begin_ap': 'a',
               'end_hh': '0',
               'end_mi': '0',
               'end_ap': 'a'}

    headers = {
        'Referer': 'https://oscar.gatech.edu/bprod/bwckgens.p_proc_term_date',
        'Cookie': 'BIGipServer~BANNER~oscar.coda_443=572230154.64288.0000'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    classes = response.text

    crn_re = re.compile(rf"\/bprod\/bwckschd\.p_disp_detail_sched\?term_in={term}&amp;crn_in=(?P<crn>[0-9]+)")

    crns = crn_re.findall(classes)

    class_re = re.compile(
        r"<caption class=\"captiontext\">Detailed Class Information</caption>\s+<tr>\s+<th CLASS=\"ddlabel\" scope=\"row\" *>(?P<title>.+?) - [0-9]+ - (?P<class>.+?) -.+labeltext\">Seats</SPAN></th>\s+<td CLASS=\"dddefault\">(?P<seat_capacity>[0-9]+)</td>\s+<td CLASS=\"dddefault\">(?P<seat_actual>[0-9]+)</td>\s+<td CLASS=\"dddefault\">(?P<seat_remaining>-*[0-9]+).+?Waitlist Seats</SPAN></th>\s+<td CLASS=\"dddefault\">(?P<wl_capacity>[0-9]+)</td>\s+<td CLASS=\"dddefault\">(?P<wl_actual>[0-9]+)</td>\s+<td CLASS=\"dddefault\">(?P<wl_remaining>-*[0-9]+)",
        re.DOTALL)

    class_recs = []
    class_dict = {}

    for crn in crns:
        r = requests.get(f"https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched",
                         {'term_in': term, 'crn_in': crn})
        class_info = r.text
        class_data = class_re.search(class_info)
        class_rec: ClassRec = {
            'title': class_data.group('title'),
            'crn': crn,
            'term': term,
            'dept_course_nbr': class_data.group('class'),
            'dept': class_data.group('class').split(' ')[0],
            'course_nbr': class_data.group('class').split(' ')[1],
            'seat_capacity': int(class_data.group('seat_capacity')),
            'seat_actual': int(class_data.group('seat_actual')),
            'seat_remaining': int(class_data.group('seat_remaining')),
            'wl_capacity': int(class_data.group('wl_capacity')),
            'wl_actual': int(class_data.group('wl_actual')),
            'wl_remaining': int(class_data.group('wl_remaining')) if crn != '89987' else 1, # TODO: fix before production
            'subscribers': []
        }
        class_recs.append(class_rec.copy())
        class_dict[crn] = class_rec

    return class_recs, class_dict


def send_message(db: firestore.firestore.Client, term: str, crn: str, dept_course_nbr: str, num_avail: int,
                 test_mode: bool):
    topic = f'{term}_{crn}{"_test" if test_mode else ""}'
    notif = messaging.Notification()
    notif.body = f'{dept_course_nbr} - {crn} has {num_avail} spot{"s" if num_avail > 1 else ""} available.'
    notif.title = 'Waitlist spot available'
    message = messaging.Message(
        notification=notif,
        topic=topic
    )
    messaging.send(message)

    reg_db = db.collection('subscriptions').where('topic', '==', topic).stream()
    reg_tokens = []
    for rec in reg_db:
        data = rec.to_dict()
        reg_tokens.append(data['token'])
    num_iters = math.ceil(len(reg_tokens) / 1000)

    for i in range(num_iters):
        messaging.unsubscribe_from_topic(reg_tokens[i * 1000:(i + 1) * 1000], topic)


def compare_docs_and_notify(db: firestore.firestore.Client, current_data: dict, old_data, test_mode: bool = False):
    notifications = []
    for doc in old_data:
        data = doc.to_dict() if type(doc) is not dict else doc
        if data['crn'] in current_data.keys():
            if current_data[data['crn']]['wl_remaining'] > 0 and data['wl_remaining'] <= 0:
                notifications.append(True)
                print(current_data)
                send_message(db, data['term'], data['crn'], data['dept_course_nbr'], current_data[data['crn']]['wl_remaining'], test_mode)
            else:
                notifications.append(False)
        else:
            notifications.append(False)
    return notifications


def main():
    fb = firebase_admin.initialize_app()
    db = firestore.client()

    isye_list, isye_dict = get_classes('ISYE', os.getenv('TERM'))
    cs_list, cs_dict = get_classes('CS', os.getenv('TERM'))
    mgt_list, mgt_dict = get_classes('MGT', os.getenv('TERM'))

    subjects = [isye_list, cs_list, mgt_list]

    isye_docs = db.collection(os.getenv('TERM')).where('dept', '==', 'ISYE').stream()
    cs_docs = db.collection(os.getenv('TERM')).where('dept', '==', 'CS').stream()
    mgt_docs = db.collection(os.getenv('TERM')).where('dept', '==', 'MGT').stream()

    compare_docs_and_notify(db, isye_dict, isye_docs)
    compare_docs_and_notify(db, cs_dict, cs_docs)
    compare_docs_and_notify(db, mgt_dict, mgt_docs)

    for subj in subjects:
        for cl in subj:
            doc_ref = db.collection(cl['term']).document(cl['crn'])
            doc_ref.set(cl)

    print(subjects)


if __name__ == '__main__':
    main()
