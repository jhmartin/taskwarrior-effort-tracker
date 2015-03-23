#!/usr/bin/env python
#
# Writes task effort log to LEDGERFILE.  Format is:
# 2015/03/22,e28087e9-525e-403c-9c4b-1aed53809092,9,no project,test3
# Date,UID,Seconds effort, Project name (or 'no project'), task description
#
# You need to adjust LEDGERFILE, or set the TIMELOG environment variable.
# Based on https://gist.github.com/wbsch/d977b0ac29aa1dfa4437
#

import calendar
import json
import os
import re
import sys
from datetime import datetime
from datetime import timedelta


LEDGERFILE = '/Users/jhmartin/.task/timetrack.ledger'

if 'TIMELOG' in os.environ:
    LEDGERFILE = os.environ['TIMELOG']

def adjust_date(d, adjust_by):
    if not isinstance(d, datetime):
        d = tw_to_dt(d)
    d -= timedelta(minutes=int(adjust_by))
    return d

def tw_to_dt(s):
    """ Taskwarrior JSON date ---> datetime object. """
    return datetime.strptime(s, "%Y%m%dT%H%M%SZ")

def dt_to_tw(d):
    """ datetime object ---> Taskwarrior JSON date. """
    return d.strftime("%Y%m%dT%H%M%SZ")


old = json.loads(sys.stdin.readline())
new = json.loads(sys.stdin.readline())

annotation_added = ('annotations' in new and not 'annotations' in old) \
                    or \
                 ('annotations' in new and 'annotations' in old and \
                  len(new['annotations']) > len(old['annotations']))


# task started
if ('start' in new and not 'start' in old) and annotation_added:
    new['annotations'].sort(key=lambda anno: anno['entry'])
    m = re.match('^[0-9]+$', new['annotations'][-1]['description'])
    if m:
        new['start'] = dt_to_tw(adjust_date(new['start'], int(m.group(0))))
        new['annotations'] = new['annotations'][:-1]
        if not new['annotations']:
            del new['annotations']
        print("Timelog: Started task %s minutes ago." % m.group(0))

        if tw_to_dt(new['start']) < tw_to_dt(new['entry']):
            new['entry'] = new['start']

# task stopped
if 'start' in old and not 'start' in new:
    started_utc = tw_to_dt(old['start'])
    started_ts = calendar.timegm(started_utc.timetuple())
    started = datetime.fromtimestamp(started_ts)
    stopped = datetime.now()
    delta = (stopped - started).total_seconds()

    if annotation_added:
        new['annotations'].sort(key=lambda anno: anno['entry'])
        m = re.match('^[0-9]+$', new['annotations'][-1]['description'])
        if m:
            new['annotations'] = new['annotations'][:-1]
            if not new['annotations']:
                del new['annotations']
            stopped = adjust_date(stopped, m.group(0))
            if stopped < started:
                print("ERROR: Stop date -%s minutes would be before the start date!" % m.group(0))
                sys.exit(1)
            print("Timelog: Stopped task %s minutes ago." % m.group(0))

    newentry = started.strftime("%Y/%m/%d") + ","
    newentry += new['uuid'] + ","
    newentry += str(int(delta)) + ","
    projectlabel= new['project'].replace('.', ':') if 'project' in new else "no project"
    newentry += projectlabel
    newentry += ","
    newentry += new['description'] + "\n"

print(json.dumps(new)
