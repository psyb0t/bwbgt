#!/usr/bin/env python
import os
import sys
import uuid
import pickle

from random import choice, shuffle
from time import time, sleep

TASK_DIR = '/tmp/.bwbgp-task-queue'

if not os.path.isdir(TASK_DIR):
    if not os.makedirs(TASK_DIR):
        raise Exception('Could not find or create task directory')


def add_task(func, args=[]):
    if not callable(func):
        raise Exception('Invalid function passed to param func')

    task_ids = os.listdir(TASK_DIR)

    while True:
        task_id = str(uuid.uuid4())
        if task_id not in task_ids:
            break

    with open(task_file(task_id), 'wb') as f:
        pickle.dump({
            'id': task_id,
            'function': func,
            'function_args': args,
            'status': 'IDLE',
            'result': '',
            'start_time': 0,
            'end_time': 0
        }, f)

    return task_id


def run_task(task_id):
    task_exists(task_id)

    with open(task_file(task_id), 'rb') as f:
        task_data = pickle.load(f)

    pid = os.fork()
    if not pid:
        func = task_data['function']
        func_args = task_data['function_args']

        with open(task_file(task_id), 'wb') as f:
            task_data['status'] = 'RUNNING'
            pickle.dump(task_data, f)

        task_data['start_time'] = int(time())
        try:
            result = func(*func_args)
        except Exception as e:
            result = 'Exception: %s' % str(e)

        with open(task_file(task_id), 'wb') as f:
            task_data['result'] = result
            task_data['status'] = 'COMPLETE'
            task_data['end_time'] = int(time())

            pickle.dump(task_data, f)

        os._exit(0)


def task_ready(task_id):
    task_exists(task_id)
    task_data = task_details(task_id)
    if task_data['status'] == 'COMPLETE':
        return True

    return False


def task_details(task_id):
    task_exists(task_id)
    return read_task_file(task_id)


def remove_task(task_id):
    os.remove(task_file(task_id))
    return


def read_task_file(task_id, t=2):
    c = 1
    while True:
        try:
            with open(task_file(task_id), 'rb') as f:
                return pickle.load(f)
        except:
            sleep(1)
            if c >= t:
                break
            c += 1
            continue

    raise Exception('Could not open task file')


def task_exists(task_id):
    if not os.path.isfile(task_file(task_id)):
        raise Exception('Inexistent task')


def task_file(task_id):
    return '%s/%s.task' % (TASK_DIR, task_id)
