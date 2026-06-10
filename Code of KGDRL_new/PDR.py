import torch
import random
import numpy as np
import pandas as pd
from new_env import JSRS

def trantime(action):
    if action is None:
        time = 0
    else:
        m = action[0]
        s = action[2]
        time = m.stage_setup_time['{}-{}'.format(m.current_stage.id, s.id)]
    return time

def STSP(in_list, data_file='Data/new/'):
    #shortest transfer then shortest process
    makespan_l = []
    for instance in in_list:
        env = JSRS.make(instance, data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                transfer = np.array([op[0].stage_setup_time['{}-{}'.format(op[0].current_stage.id,
                                                                           op[2].id)] for op in operations]).reshape(-1)
                process = np.array([op[1].average_processing_time[op[2]] for op in operations]).reshape(-1)
                                    # * op[0].speed[op[2]] for op in operations]).reshape(-1)
                avail = [True if i == 0 else False for i in transfer]
                try:
                    true_avail = process[avail]
                    true_op = [op for op, bo in zip(operations, avail) if bo == True]
                    index = np.argmin(true_avail)
                    action = true_op[index]
                except:
                    total = [tr+pr for tr, pr in zip(transfer, process)]
                    index = total.index(min(total))
                    action = operations[index]
            next_status = env.step(action)
            status = next_status
        makespan_l.append(env.makespan)
    return makespan_l

def STTP(in_list,data_file='Data/new/'):
    # shortest transfer time prior
    makespan_l = []
    for instance in in_list:
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                transfer = [op[0].stage_setup_time['{}-{}'.format(op[0].current_stage.id, op[2].id)] for op in operations]
                index = transfer.index(min(transfer))
                action = operations[index]
            next_status = env.step(action)
            status = next_status
        makespan_l.append(env.makespan)
    return makespan_l


def Random(in_list,data_file='Data/new/'):
    makespan_l = []
    transfer_l = []
    for instance in in_list:
        transfer = 0
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        random.seed(0)
        while not status.done:
            operations = status.available_operations
            operations.append(None)
            action = random.choice(operations)
            '''if None in operations and len(operations) == 1:
                action = None
            else:
                random.seed(0)
                action = random.choice(operations)'''
            transfer += trantime(action)
            next_status = env.step(action)
            status = next_status
        transfer_l.append(transfer)
        makespan_l.append(env.makespan)
        timedata = pd.DataFrame({'transfer': transfer_l, 'makespan': makespan_l})
        timedata.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/random.csv')
    return makespan_l


def FIFO(in_list,data_file='Data/new/'):
    # first in first out
    makespan_l = []
    transfer_l = []
    for instance in in_list:
        transfer = 0
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            # Choose the first available operation
            action = operations[0]
            transfer += trantime(action)
            next_status = env.step(action)
            status = next_status
        transfer_l.append(transfer)
        makespan_l.append(env.makespan)
        timedata = pd.DataFrame({'transfer': transfer_l, 'makespan': makespan_l})
        timedata.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/FIFO.csv')
    return makespan_l

def SPT(in_list,data_file='Data/new/'):
    # shortest processing time
    makespan_l = []
    transfer_l = []
    for instance in in_list:
        transfer = 0
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                # Choose the shortest processing time operation
                process = [op[1].average_processing_time[op[2]] for op in operations] # * op[0].speed[op[2]]
                index = process.index(min(process))
                action = operations[index]
            transfer += trantime(action)
            next_status = env.step(action)
            status = next_status
        transfer_l.append(transfer)
        makespan_l.append(env.makespan)
        timedata = pd.DataFrame({'transfer': transfer_l, 'makespan': makespan_l})
        timedata.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/SPT.csv')
    return makespan_l

def LPT(in_list,data_file='Data/new/'):
    # longest processing time
    makespan_l = []
    for instance in in_list:
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                # Choose the longest processing time operation
                process = [op[1].average_processing_time[op[2]] * op[0].speed[op[2]] for op in operations]
                index = process.index(max(process))
                action = operations[index]
            next_status = env.step(action)
            status = next_status
        makespan_l.append(env.makespan)
    return makespan_l

def SPTT(in_list,data_file='Data/new/'):
    # shortest processing time then transfer time
    makespan_l = []
    for instance in in_list:
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                # Choose the shortest processing+transfer time operation
                transfer = [op[0].stage_setup_time['{}-{}'.format(op[0].current_stage.id, op[2].id)] for op in operations]
                process = [op[1].average_processing_time[op[2]] for op in operations]
                           # * op[0].speed[op[2]] for op in operations]
                total = [tr+pr for tr, pr in zip(transfer, process)]
                index = total.index(min(total))
                action = operations[index]
            next_status = env.step(action)
            status = next_status
        makespan_l.append(env.makespan)
    return makespan_l

def LPTT(in_list,data_file='Data/new/'):
    # longest processing+transfer time operation
    makespan_l = []
    for instance in in_list:
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                # Choose the shortest processing+transfer time operation
                transfer = [op[0].stage_setup_time['{}-{}'.format(op[0].current_stage.id, op[2].id)] for op in operations]
                process = [op[1].average_processing_time[op[2]] for op in operations]
                           # * op[0].speed[op[2]] for op in operations]
                total = [tr + pr for tr, pr in zip(transfer, process)]
                index = total.index(max(total))
                action = operations[index]
            next_status = env.step(action)
            status = next_status
        makespan_l.append(env.makespan)
    return makespan_l

def MOR(in_list,data_file='Data/new/'):
    # most operations remaining
    makespan_l = []
    for instance in in_list:
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                ope_remain = [len(op[1].stages) for op in operations]
                index = ope_remain.index(max(ope_remain))
                action = operations[index]
            next_status = env.step(action)
            status = next_status
        makespan_l.append(env.makespan)
    return makespan_l

def MWKR(in_list,data_file='Data/new/'):
    # most work time remaining
    makespan_l = []
    transfer_l = []
    for instance in in_list:
        transfer = 0
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                protime_remain = [sum(op[1].average_processing_time[s_remain] for s_remain in op[1].stages) for op in operations]
                index = protime_remain.index(max(protime_remain))
                action = operations[index]
            transfer += trantime(action)
            next_status = env.step(action)
            status = next_status
        transfer_l.append(transfer)
        makespan_l.append(env.makespan)
        timedata = pd.DataFrame({'transfer': transfer_l, 'makespan': makespan_l})
        timedata.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/MWKR.csv')
    return makespan_l


def SWKR(in_list,data_file='Data/new/'):
    # shortest working time remaining
    makespan_l = []
    for instance in in_list:
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                protime_remain = [sum(op[1].average_processing_time[s_remain] for s_remain in op[1].stages) for op in
                                  operations]
                index = protime_remain.index(min(protime_remain))
                action = operations[index]
            next_status = env.step(action)
            status = next_status
        makespan_l.append(env.makespan)
    return makespan_l


def SSO(in_list,data_file='Data/new/'):
    # shortest processing time of subsequent operation
    makespan_l = []
    transfer_l = []
    for instance in in_list:
        transfer = 0
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                protime_so = [op[1].average_processing_time[op[1].stages[1]] if len(op[1].stages) > 1 else 1000 for op in operations]
                index = protime_so.index(min(protime_so))
                action = operations[index]
            transfer += trantime(action)
            next_status = env.step(action)
            status = next_status
        transfer_l.append(transfer)
        makespan_l.append(env.makespan)
        timedata = pd.DataFrame({'transfer': transfer_l, 'makespan': makespan_l})
        timedata.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/SSO.csv')
    return makespan_l


def LSO(in_list,data_file='Data/new/'):
    # longest processing time of subsequent operation
    makespan_l = []
    for instance in in_list:
        env = JSRS.make(instance,data_file+instance+'.jsr')
        status = env.reset()
        while not status.done:
            operations = status.available_operations
            if None in operations and len(operations) == 1:
                action = None
            else:
                protime_so = [op[1].average_processing_time[op[1].stages[1]] if len(op[1].stages) > 1 else 0 for op in operations]
                index = protime_so.index(max(protime_so))
                action = operations[index]
            next_status = env.step(action)
            status = next_status
        makespan_l.append(env.makespan)
    return makespan_l





if __name__ == '__main__':
    instance_names = ['IS{}J{}M{}R{}'.format(3, 5, 5, i+10) for i in range(10)]
    print(Random(in_list=instance_names))


