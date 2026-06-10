import random
import numpy as np
import pandas as pd
from tqdm import tqdm
import torch
import math
from torch import nn
from new_env import Job, Machine, JSRS, JSRSInstance, JSRSStatus, Stage
from sklearn.preprocessing import normalize
import torch.nn.functional as F
import matplotlib.pyplot as plt

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

def ope_process_time(j_id, s_id, status):
    df = pd.DataFrame(0, index=j_id, columns=s_id)
    for item in status.operation_records:
        if item[0] is not None:
            m, j, s = item[0]
            df.loc[item[0][1], item[0][2]] = m.stage_setup_time['{}-{}'.format(m.current_stage.id, s.id)]+\
                                             j.average_processing_time[s] * m.speed[s]
    return np.array(df)


def Machine_feature(status:JSRSStatus): # (working_binary, m_neighbor, avail_time, utility, current, speed)
    # 机器特征
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

    return machine_f # (working_binary, m_neighbor, avail_time, utility, current, speed)

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


class PolicyNet(torch.nn.Module):
    def __init__(self, state_dim, hidden_dim, action_dim, action_bound=1):
        super(PolicyNet, self).__init__()
        self.fc1 = torch.nn.Linear(state_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, action_dim)
        self.action_bound = action_bound  # action_bound是环境可以接受的动作最大值

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return F.relu(self.fc2(x)) * self.action_bound


class QValueNet(torch.nn.Module):
    def __init__(self, state_dim, hidden_dim, action_dim):
        super(QValueNet, self).__init__()
        self.fc1 = torch.nn.Linear(state_dim + action_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, hidden_dim)
        self.fc_out = torch.nn.Linear(hidden_dim, 1)

    def forward(self, x, a):
        cat = torch.cat([x, a], dim=1) # 拼接状态和动作
        x = F.relu(self.fc1(cat))
        x = F.relu(self.fc2(x))
        return self.fc_out(x)

class DDPG:
    ''' DDPG算法 '''
    def __init__(self, state_dim, hidden_dim, action_dim,  actor_lr, critic_lr,
                 action_bound=1, sigma=0.01, tau=0.005, gamma=0.98):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.actor = PolicyNet(state_dim, hidden_dim, action_dim, action_bound).to(self.device)
        self.critic = QValueNet(state_dim, hidden_dim, action_dim).to(self.device)
        self.target_actor = PolicyNet(state_dim, hidden_dim, action_dim, action_bound).to(self.device)
        self.target_critic = QValueNet(state_dim, hidden_dim, action_dim).to(self.device)
        # 初始化目标价值网络并设置和价值网络相同的参数
        self.target_critic.load_state_dict(self.critic.state_dict())
        # 初始化目标策略网络并设置和策略相同的参数
        self.target_actor.load_state_dict(self.actor.state_dict())
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=actor_lr)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=critic_lr)
        self.gamma = gamma
        self.sigma = sigma  # 高斯噪声的标准差,均值直接设为0
        self.tau = tau  # 目标网络软更新参数
        self.action_dim = action_dim


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
        return node, state_vec

    def take_action(self, status):
        operation = self.get_state_vec(status)[0]
        state = np.array(self.get_state_vec(status)[1])
        ope_raw = [(x[0], x[1]) if x is not None else None for x in status.available_operations]
        ope = []
        for oper in ope_raw:
            if oper not in ope:
                ope.append(oper)
        avail = [1 if elem in ope else 0 for elem in operation]
        avail = torch.tensor(avail, dtype=torch.float).to(self.device).unsqueeze(1)
        probs = self.actor(torch.tensor(state, dtype=torch.float).to(self.device)).view(-1, 1)
        probs = probs * avail + 1e-6
        action_probs = F.normalize(probs, p=1, dim=0)
        action_dist = torch.distributions.Categorical(action_probs.squeeze())
        action_num = action_dist.sample().item()
        action_node = operation[action_num]
        action = [item for item in status.available_operations if
                  item is not None and item[0] == action_node[0] and item[1] == action_node[1]]
        action = action[0] if len(action) == 1 else None
        old_probs = np.array(action_probs.detach().cpu().numpy()).reshape(1, -1)
        # 把none_action的概率均匀离散到所有不可用的动作上面，形成一个Ns*Nm*Nj的张量
        return action, action_num, old_probs, avail.detach().cpu().numpy()


    def soft_update(self, net, target_net):
        for param_target, param in zip(target_net.parameters(), net.parameters()):
            param_target.data.copy_(param_target.data * (1.0 - self.tau) + param.data * self.tau)

    def update(self, transition_dict):
        states = torch.tensor(transition_dict['states'], dtype=torch.float).to(self.device)
        actions = torch.tensor(transition_dict['action_probs'], dtype=torch.float).to(self.device)
        rewards = torch.tensor(transition_dict['rewards'], dtype=torch.float).view(-1, 1).to(self.device)
        next_states = torch.tensor(transition_dict['next_states'], dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict['dones'], dtype=torch.float).view(-1, 1).to(self.device)

        states = states.squeeze(1)
        actions = actions.squeeze(1)
        next_states = next_states.squeeze(1)
        next_q_values = self.target_critic(next_states, self.target_actor(next_states))
        q_targets = rewards + self.gamma * next_q_values * (1 - dones)
        critic_loss = torch.mean(F.mse_loss(self.critic(states, actions), q_targets))
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        actor_loss = -torch.mean(self.critic(states, self.actor(states)))
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        self.soft_update(self.actor, self.target_actor)  # 软更新策略网络
        self.soft_update(self.critic, self.target_critic)  # 软更新价值网络

    def train_loop(self, instance_list, episodes=200, plot_process=True):
        return_l = []
        makespan_l = []
        instances_makespan = []
        for i in range(10):
            with tqdm(total=int(episodes / 10), desc='Iteration %d' % i) as pbar:
                for i_episode in range(int(episodes / 10)):
                    episode_return, episode_makespan = [], []
                    transition_dict = {
                        'states': [],
                        'action_list': [],
                        'action_num': [],
                        'action_probs': [],
                        'avail': [],
                        'next_states': [],
                        'rewards': [],
                        'dones': []
                    }
                    for instance in instance_list:
                        instance_reward = 0
                        env: JSRSInstance = JSRS.make(instance, 'Data/new/' + instance + '.jsr')
                        status = env.reset()
                        while not status.done:
                            states_vec = self.get_state_vec(status)[1]
                            action, action_num, action_probs, avail = self.take_action(status)
                            tran_time = trantime(action)
                            next_status = env.step(action)
                            next_state = self.get_state_vec(next_status)[1]
                            reward = state_reward(status, next_status, action)
                            instance_reward += reward - tran_time
                            if action is None:
                                instance_reward -= 500
                            transition_dict['states'].append(states_vec)
                            transition_dict['action_list'].append(action)
                            transition_dict['action_num'].append(action_num)
                            transition_dict['action_probs'].append(action_probs)
                            transition_dict['avail'].append(avail)
                            transition_dict['next_states'].append(next_state)
                            transition_dict['rewards'].append(reward)
                            transition_dict['dones'].append(env.done)
                            status = next_status
                        instance_reward = instance_reward*0.01 - env.makespan
                        episode_makespan.append(env.makespan)
                        episode_return.append(instance_reward)
                    self.update(transition_dict)
                    return_l.append(sum(episode_return) / len(episode_return))
                    makespan_l.append(episode_makespan)
                    instance_makespan = sum(episode_makespan)/len(episode_makespan)
                    instances_makespan.append(instance_makespan)
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


        if plot_process:
            plt.plot(return_l)
            plt.xlabel('Episodes')
            plt.ylabel('Average Returns')
            plt.title('DDPG')
            plt.show()

            min_makespan = min(instances_makespan)
            plt.plot(instances_makespan)
            plt.xlabel('Episodes')
            plt.ylabel('Average Makespan')
            plt.ylim(min_makespan-50, min_makespan+300)
            plt.title('DDPG (Min makespan: {})'.format(min(instances_makespan)))
            plt.show()

        return return_l, makespan_l, instances_makespan

if __name__ == '__main__':
    # 训练
    random.seed(0)
    np.random.seed(0)
    torch.manual_seed(0)

    my_dvl = DDPG(hidden_dim=64, state_dim=5*5*12, action_dim=5*5, actor_lr=5e-4, critic_lr=1e-5)
    instance_names = ['IS{}J{}M{}R{}'.format(3, 5, 5, i+10) for i in range(10)]
    return_list, makespan_list, instance_makespan = my_dvl.train_loop(instance_list=instance_names, episodes=100)