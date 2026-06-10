from tqdm import tqdm
from copy import deepcopy
from new_env import JSRS, JSRSInstance, JSRSStatus, Stage, Machine, Job
import random
import numpy as np
import pandas as pd
import collections
import torch
import math
import torch.nn.functional as F
from matplotlib import pyplot as plt
from sklearn.preprocessing import normalize

def trantime(action):
    if action is None:
        time = 0
    else:
        m = action[0]
        s = action[2]
        time = m.stage_setup_time['{}-{}'.format(m.current_stage.id, s.id)]
    return time

def evaluate_max_makespan(status: JSRSStatus):

    max_makespan = 0
    for stage in status.stage_register.values():
        tran_pro, process, stage_id = [], [], []
        for job in stage.unscheduled_jobs:
            process.append(job.average_processing_time[stage])
        for m in stage.all_machines:
            tran_pro.append(m.stage_setup_time['{}-{}'.format(m.current_stage.id, stage.id)] * len(process)
                            + sum(process) * m.speed[stage])
        max_makespan += max(tran_pro)
    return max_makespan


def state_reward(status: JSRSStatus, next_status: JSRSStatus, action):
    if action is None:
        reward = 0  # processing = 0, status remain same
    else:
        machine: Machine = action[0]
        job: Job = action[1]
        stage: Stage = action[2]
        processing = machine.stage_setup_time['{}-{}'.format(machine.current_stage.id, stage.id)] + \
                     job.average_processing_time[stage] * machine.speed[stage]
        reward = evaluate_max_makespan(status)-(evaluate_max_makespan(next_status) + processing)
    return reward


class ReplayBuffer:
    """ 经验回放池 """

    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)  # 队列,先进先出

    def add(self, _state, _reward, _next_state, _done):  # 将数据加入buffer
        self.buffer.append((_state, _reward, _next_state, _done))

    def sample(self, _batch_size):  # 从buffer中采样数据,数量为batch_size
        transitions = random.sample(self.buffer, _batch_size)
        _state, _reward, _next_state, _done = zip(*transitions)
        return np.array(_state), _reward, np.array(_next_state), _done

    def size(self):  # 目前buffer中数据的数量
        return len(self.buffer)


class VNet(torch.nn.Module):
    """ 只有一层隐藏层的Q网络 """

    def __init__(self, state_d, hidden_d):
        super(VNet, self).__init__()
        self.fc1 = torch.nn.Linear(state_d, hidden_d)
        self.fc2 = torch.nn.Linear(hidden_d, hidden_d)
        self.fc3 = torch.nn.Linear(hidden_d, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))  # 隐藏层使用ReLU激活函数
        x = F.relu(self.fc2(x))
        return self.fc3(x)


def ope_process_time(j_id, s_id, status):
    df = pd.DataFrame(0.0, index=j_id, columns=s_id)
    for item in status.operation_records:
        if item[0] is not None:
            m, j, s = item[0]
            df.loc[item[0][1], item[0][2]] = m.stage_setup_time['{}-{}'.format(m.current_stage.id, s.id)]+\
                                             j.average_processing_time[s] * m.speed[s]
    return np.array(df)


def Machine_feature(status:JSRSStatus):
    m_id = [m for m in status.machine_register.values()]
    working_binary = [1 if m.current_task == None else 0 for m in m_id]
    avail_time = [m.next_finishing_time for m in m_id]
    avail_time = [avail_time[i]*(1-working_binary[i]) for i in range(len(working_binary))]
    avail_time = [status.clock if math.isnan(x) else x for x in avail_time]
    m_stage = [m.current_stage for m in m_id]
    m_neighbor = [len(s.unscheduled_jobs) for s in m_stage]
    working_time = [sum(note[2]-note[1] if len(note) == 3 else status.clock-note[1] for note in m.logs) if len(m.logs) > 0 else 0 for m in m_id]
    utility = [1-(work+1)/(status.clock+1) for work in working_time]
    current = [int(str(m.current_stage)[-1]) for m in m_id]
    speed = [m.speed[m.current_stage] for m in m_id]
    machine_f = (working_binary, m_neighbor, avail_time, utility, current, speed)

    return machine_f

def Job_feature(status:JSRSStatus):
    j_id = [j for j in status.job_register.values()]
    s_id = [s for s in status.stage_register.values()]
    process_binary = [1 if j.status == 'waiting' else 0 for j in j_id]
    j_neighbor = []
    for j in j_id:
        try:
            j_stage = j.stages[0]
            j_neighbor.append(len(j_stage.all_machines))
        except:
            j_neighbor.append(0)
    avail_time = [j.available_time if j.status == 'processing' else status.clock for j in j_id]  #job_avail_time(j_id, s_id, status)[0]
    utility_raw = (ope_process_time(j_id, s_id, status).sum(axis=1)+1)/(status.clock+1)
    utility = [1 if u > 1 else u for u in utility_raw]
    current = [4 if job.current_stage == None else int(str(job.current_stage)[-1]) for job in j_id]
    speed = [1 for _ in j_id]
    job_f = (process_binary, j_neighbor, avail_time, utility, current, speed)

    return job_f




class DQN:
    """ Deep Q Learning."""

    def __init__(self, state_dim=25*12, hidden_dim=None, learning_rate=1e-3, gamma=0.98, epsilon=0.05,
                 _target_update=10):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        print('Device: ', self.device)
        '''state_d = (len(env.machine_register.keys()) + len(env.job_register.keys())) * (
                len(env.stage_register.keys()) + 2)'''
        state_d = state_dim
        hidden_d = state_d * 5 if hidden_dim is None else hidden_dim
        self.v_net = VNet(state_d, hidden_d).to(self.device)
        self.target_v_net = VNet(state_d, hidden_d).to(self.device)
        # 使用Adam优化器
        self.optimizer = torch.optim.Adam(self.v_net.parameters(),
                                          lr=learning_rate)
        self.gamma = gamma  # 折扣因子
        self.epsilon = epsilon  # epsilon-贪婪策略
        self.target_update = _target_update  # 目标网络更新频率
        self.count = 0  # 计数器,记录更新次数

    def get_state_vec(self, status: JSRSStatus):
        job_feature = np.array(Job_feature(status)).T
        machine_feature = np.array(Machine_feature(status)).T
        node, vec = [], []
        for i in range(machine_feature.shape[0]):
            for j in range(job_feature.shape[0]):
                vec.append(np.hstack((machine_feature[i], job_feature[j])))
        for x in status.machine_register.values():
            for y in status.job_register.values():
                node.append((x, y))
        vec = np.array(vec)
        vec_normalized = normalize(vec, axis=0)
        state_vec = vec_normalized.reshape(1, -1)
        ope_raw = [(x[0], x[1]) if x is not None else None for x in status.available_operations]
        ope = []
        for oper in ope_raw:
            if oper not in ope:
                ope.append(oper)
        # dimension : 1*(Nm*Nj*12),1*(Nm*Nj*12),1*(Nm*Nj),1*(Nm*Nj)
        return state_vec

    def take_action(self, env, status, epsilon_greedy=True):  # epsilon-贪婪策略采取动作
        if random.random() < self.epsilon and epsilon_greedy:
            action = random.choice(status.available_operations)
        else:
            next_state_values = []
            all_idx = list(range(len(status.available_operations)))
            random.shuffle(all_idx)
            for i in all_idx:
                env_tmp = deepcopy(env)
                available_operations = env_tmp.find_available_operations()
                if available_operations[i] is None:
                    next_status = status
                else:
                    next_status = env_tmp.step(available_operations[i], show_status=False)
                next_state = torch.tensor(self.get_state_vec(next_status), dtype=torch.float).to(self.device)
                next_state_values.append(self.v_net(next_state).item())
            best_idx = all_idx[next_state_values.index(max(next_state_values))]
            action = status.available_operations[best_idx]

        return action

    def update(self, transition_dict):
        states = torch.tensor(transition_dict['states'],
                              dtype=torch.float).to(self.device)
        rewards = torch.tensor(transition_dict['rewards'],
                               dtype=torch.float).view(-1, 1).to(self.device)
        next_states = torch.tensor(transition_dict['next_states'],
                                   dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict['dones'],
                             dtype=torch.float).view(-1, 1).to(self.device)

        s_values = self.v_net(states).squeeze(2)
        ns_values = self.target_v_net(next_states).squeeze(2)
        # 下个状态的最大Q值
        v_targets = rewards + self.gamma * ns_values * (1 - dones)  # TD误差目标，使用(1 - dones)来锚定最后状态的价值。
        dqn_loss = torch.mean(F.mse_loss(s_values, v_targets))  # 均方误差损失函数
        self.optimizer.zero_grad()  # PyTorch中默认梯度会累积,这里需要显式将梯度置为0
        dqn_loss.backward()  # 反向传播更新参数
        self.optimizer.step()

        if self.count % self.target_update == 0:
            self.target_v_net.load_state_dict(
                self.v_net.state_dict())  # 更新目标网络
        self.count += 1

    def train_loop(self, buffer_size=2048, minimal_buffer_size=128, batch_size=64, instance_list=None, episodes=500,
                   plot_process=True,val_process=False, val_data=None):
        replay_buffer = ReplayBuffer(buffer_size)
        return_l = []
        makespan_l = []
        instances_makespan = []
        #makespan_data = pd.DataFrame()
        #trantime_data = pd.DataFrame()
        val_final_makespan = pd.DataFrame()
        val_final_trantime = pd.DataFrame()

        num = 0
        for i in range(10):
            with tqdm(total=int(episodes / 10), desc='Iteration %d' % i) as pbar:
                for i_episode in range(int(episodes / 10)):
                    episode_return, episode_makespan, episode_tran_time = [], [], []
                    for instance in instance_list:
                        instance_reward = 0
                        tran_total = 0
                        env: JSRSInstance = JSRS.make(instance, 'Data/new/' + instance + '.jsr')
                        status = env.reset()
                        while not status.done:
                            state = self.get_state_vec(status)
                            operation = self.take_action(env, status)
                            tran_time = trantime(operation)
                            next_status = env.step(operation)
                            next_state = self.get_state_vec(next_status)
                            reward = state_reward(status, next_status, operation)-tran_time
                            if operation is None:
                                reward -= 500
                            replay_buffer.add(state, reward, next_state, env.done)
                            status = next_status
                            instance_reward += reward
                            tran_total += tran_time
                        if replay_buffer.size() > minimal_buffer_size:
                            b_s, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                            transition_dict = {
                                'states': b_s,
                                'next_states': b_ns,
                                'rewards': b_r,
                                'dones': b_d
                            }
                            self.update(transition_dict)
                        instance_reward = instance_reward * 0.01 - env.makespan
                        episode_makespan.append(env.makespan)
                        episode_return.append(instance_reward)
                        episode_tran_time.append(tran_total)
                    return_l.append(sum(episode_return) / len(episode_return))
                    #makespan_data[num] = episode_makespan
                    #trantime_data[num] = episode_tran_time
                    makespan_l.append(episode_makespan)
                    instance_makespan = sum(episode_makespan) / len(episode_makespan)
                    instances_makespan.append(instance_makespan)
                    num += 1
                    if (i_episode + 1) % 10 == 0:
                        pbar.set_postfix({
                            'episode':
                                '%d' % (episodes / 10 * i + i_episode + 1),
                            'return':
                                '%.3f' % np.mean(return_l[-10:]),
                            'makespan':
                                '%.3f' % np.mean(instances_makespan[-10:])
                        })
                    pbar.update(1)
                    if val_process:
                        makespan_val = []
                        trantime_val = []
                        for val_instance in val_data:
                            val_env = JSRS.make(val_instance, 'Data/val/' + val_instance + '.jsr')
                            val_status = val_env.reset()
                            vtran_total = 0
                            while not val_status.done:
                                vaction = self.take_action(val_env, val_status)
                                vtran_time = trantime(vaction)
                                val_next_status = val_env.step(vaction)
                                val_status = val_next_status
                                vtran_total += vtran_time
                            makespan_val.append(val_env.makespan)
                            trantime_val.append(vtran_total)
                        val_final_makespan[num] = makespan_val
                        val_final_trantime[num] = trantime_val
        #trantime_data.T.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/trantime_DQN.csv')
        #makespan_data.T.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/makespan_DQN.csv')
        import os
        output_dir = 'D:/记录/课程、比赛/研二/HR_based DRL in JSRS'
        if os.path.exists(output_dir):
            val_final_makespan.T.to_csv(os.path.join(output_dir, 'DDQN_val_data_makespan.csv'))
            val_final_trantime.T.to_csv(os.path.join(output_dir, 'DDQN_val_data_trantime.csv'))
        if plot_process:

            mv_return = moving_average(return_l, 9)
            plt.plot(mv_return)
            plt.xlabel('Episodes')
            plt.ylabel('Returns (Average)')
            plt.title('DDQN')
            plt.show()

            min_makespan = min(instances_makespan)
            max_makespan = max(instances_makespan)
            plt.plot(moving_average(instances_makespan, 9))
            plt.xlabel('Episodes')
            plt.ylabel('Average Makespan')
            plt.ylim(min_makespan - 50, max_makespan + 50)
            plt.title('DDQN (Min makespan: {})'.format(min(instances_makespan)))
            plt.show()
        return return_l, makespan_l,instances_makespan

    '''def evaluate(self, show_status=False):
        status = self.env.reset()
        counter = 0
        while not status.done:
            operation = self.take_action(status, epsilon_greedy=False)
            if show_status:
                print('Status: ', customized_state(status))
                print('Action: ', operation)
            status = self.env.step(operation, show_status=show_status)
            counter += 1
            if counter > 500:
                print('{}求解失败'.format(self.env.name))
                break
        return self.env.makespan'''


def moving_average(a, window_size):
    cumulative_sum = np.cumsum(np.insert(a, 0, 0))
    middle = (cumulative_sum[window_size:] - cumulative_sum[:-window_size]) / window_size
    r = np.arange(1, window_size - 1, 2)
    begin = np.cumsum(a[:window_size - 1])[::2] / r
    end = (np.cumsum(a[:-window_size:-1])[::2] / r)[::-1]
    return np.concatenate((begin, middle, end))


if __name__ == '__main__':
    random.seed(0)
    np.random.seed(0)
    torch.manual_seed(0)
    my_dqn = DQN(hidden_dim=128, learning_rate=1e-4)
    instance_names = ['IS{}J{}M{}R{}'.format(3, 5, 5, i) for i in range(20)]
    val_names = ['IS{}J{}M{}R{}'.format(3, 5, 5, i) for i in range(25)]
    return_list, makespan_list, instances_makespan = my_dqn.train_loop(instance_list=instance_names, episodes=1000, val_process=True, val_data=val_names)
