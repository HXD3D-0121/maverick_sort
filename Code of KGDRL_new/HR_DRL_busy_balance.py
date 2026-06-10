import math
import torch
import random
import torch.nn.functional as F
import pandas as pd
from new_env import Job, Machine, JSRS, JSRSInstance, JSRSStatus, Stage
from sklearn.preprocessing import normalize
import numpy as np
import collections
from tqdm import tqdm
import matplotlib.pyplot as plt
import torch.nn.init as init

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

def STSP_prob(status):
    # ope: M & J of available operations
    ope = []
    operations = status.available_operations
    ope_raw = [(x[0], x[1]) for x in operations if x is not None]
    node = [(x, y) for x in status.machine_register.values() for y in status.job_register.values()]
    for oper in ope_raw:
        if oper not in ope:
            ope.append(oper)
    avail = [True if x in ope else False for x in node]
    p = torch.zeros(len(node), 1)
    if None not in operations:
        transfer = np.array([op[0].stage_setup_time['{}-{}'.format(op[0].current_stage.id,
                                                                   op[2].id)] for op in operations])

        t_vec = torch.tensor(transfer, dtype=torch.float).view(-1, 1)
        #p_transfer = F.normalize(torch.exp(-t_vec), p=1, dim=0)

        t_vec = F.normalize(t_vec, p=2, dim=0)
        p_transfer = F.normalize(torch.exp(-t_vec), p=1, dim=0)
        p[avail] = p_transfer
    return p

def busy_balance(status):
    # 根据每个可用操作对应任务的加工负荷计算平衡度概率。
    # 加工负荷（剩余阶段总加工时间）越大的任务，通过正指数变换后获得的概率越高，
    # 从而使系统优先调度高负荷任务以实现车间负载均衡。
    ope = []
    operations = status.available_operations
    ope_raw = [(x[0], x[1]) for x in operations if x is not None]
    node = [(x, y) for x in status.machine_register.values() for y in status.job_register.values()]
    for oper in ope_raw:
        if oper not in ope:
            ope.append(oper)
    avail = [True if x in ope else False for x in node]
    p = torch.zeros(len(node), 1)
    if None not in operations:
        '''stages = [str(n) for n in status.stage_register.values()]
        counts = [len(n.unscheduled_jobs) for n in status.stage_register.values()]
        jobs = [str(n) for n in status.job_register.values()]
        c_stages = [str(n.stages[0]) if len(n.stages) > 1 else None for n in status.job_register.values()]
        job_info = pd.DataFrame({'jobs': jobs, 'c_stages': c_stages})
        print(job_info)
        rates = pd.DataFrame(job_info.groupby('c_stages')['jobs'].count()).reset_index()
        print(rates)
        rates.columns = ['stages', 'counts']
        rat_value = dict(zip(stages, counts))
        p_balance = [rat_value[op[2].id] for op in operations]
        p_vec = torch.tensor(p_balance, dtype=torch.float).view(-1, 1)
        p_busy = F.normalize(p_vec, p=1, dim=0)'''
        p_balance = [sum(op[1].average_processing_time[s_remain] for s_remain in op[1].stages) for op in operations]
        p_vec = torch.tensor(p_balance, dtype=torch.float).view(-1, 1)
        p_vec = F.normalize(p_vec, p=2, dim=0)
        p_busy = F.normalize(torch.exp(p_vec), p=1, dim=0)
        p[avail] = p_busy

    return p

def moving_average(a, window_size):
    cumulative_sum = np.cumsum(np.insert(a, 0, 0))
    middle = (cumulative_sum[window_size:] - cumulative_sum[:-window_size]) / window_size
    r = np.arange(1, window_size - 1, 2)
    begin = np.cumsum(a[:window_size - 1])[::2] / r
    end = (np.cumsum(a[:-window_size:-1])[::2] / r)[::-1]
    return np.concatenate((begin, middle, end))

def compute_advantage(gamma, lmbda, td_delta):
    td_delta = td_delta.detach().numpy()
    advantage_list = []
    advantage = 0.0
    for delta in td_delta[::-1]:
        advantage = gamma * lmbda * advantage + delta
        advantage_list.append(advantage)
    advantage_list.reverse()
    return torch.tensor(advantage_list, dtype=torch.float)

class ReplayBuffer:
    """ 经验回放池 """

    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)  # 队列,先进先出

    def add(self, states, action_num, prob_guidance, prob, avail, avail_bi, rewards, next_states, dones):  # 将数据加入buffer
        self.buffer.append((states, action_num, prob_guidance, prob, avail, avail_bi, rewards, next_states, dones))

    def sample(self, _batch_size, device):  # 从buffer中采样数据,数量为batch_size
        transitions = random.sample(self.buffer, _batch_size)
        states, action_num, prob_guidance, prob, avail, avail_bi, rewards, next_states, dones = zip(*transitions)

        states = torch.tensor(states, dtype=torch.float).to(device)
        action_num = torch.tensor(action_num, dtype=torch.int64).view(-1, 1).to(device)
        prob_guidance = torch.tensor(prob_guidance, dtype=torch.float).to(device)
        prob = torch.tensor(prob, dtype=torch.float).to(device)
        avail = torch.tensor(avail, dtype=torch.float).to(device)
        avail_bi = torch.tensor(avail_bi, dtype=torch.float).to(device)
        rewards = torch.tensor(rewards, dtype=torch.float).view(-1, 1).to(device)
        next_states = torch.tensor(next_states, dtype=torch.float).to(device)
        dones = torch.tensor(dones, dtype=torch.float).view(-1, 1).to(device)
        return states, action_num, prob_guidance, prob, avail, avail_bi, rewards, next_states, dones

    def size(self):  # 目前buffer中数据的数量
        return len(self.buffer)



class PolicyNet(torch.nn.Module):
    def __init__(self, state_dim, hidden_dim, action_dim):
        super(PolicyNet, self).__init__()
        self.fc1 = torch.nn.Linear(state_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, hidden_dim*2)
        self.fc3 = torch.nn.Linear(hidden_dim*2, hidden_dim)
        self.fc4 = torch.nn.Linear(hidden_dim, action_dim)


    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return F.relu(self.fc4(x))


class ValueNet(torch.nn.Module):
    def __init__(self, state_dim, hidden_dim):
        super(ValueNet, self).__init__()
        self.fc1 = torch.nn.Linear(state_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, hidden_dim*2)
        self.fc3 = torch.nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc4 = torch.nn.Linear(hidden_dim, 1)


    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.fc4(x)



class PPO:
    def __init__(self, hidden_dim=None, actor_lr=5e-4, critic_lr=1e-5, state_d=25*12, action_d=25, gamma=0.96,
                 lmbda=0.95, epochs=15, eps=0.1, alpha1=1.0, alpha2=0.1, random_alpha=False):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        print('Device: ', self.device)
        # state由ma和job特征向量embedding而成
        state_dim = state_d
        hidden_dim = state_dim * 5 if hidden_dim is None else hidden_dim
        # 用三位数代表动作
        action_dim = action_d
        # 策略网络
        self.actor = PolicyNet(state_dim, hidden_dim, action_dim).to(self.device)
        self.critic = ValueNet(state_dim, hidden_dim).to(self.device)  # 价值网络
        # 策略网络优化器
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(),
                                                lr=actor_lr)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(),
                                                 lr=critic_lr)  # 价值网络优化器
        self.gamma = gamma
        self.lmbda = lmbda
        self.epochs = epochs    # 一条序列的数据用来训练轮数
        self.eps = eps  # PPO中截断范围的参数
        self.actor_loss = []
        self.critic_loss = []
        # 知识引导权重系数，支持固定值或随机初始化以展示可调整性
        if random_alpha:
            self.alpha1 = random.uniform(0.5, 2.0)
            self.alpha2 = random.uniform(0.05, 0.5)
            print(f'Random alpha initialized: alpha1={self.alpha1:.4f}, alpha2={self.alpha2:.4f}')
        else:
            self.alpha1 = alpha1
            self.alpha2 = alpha2

    def v_target(self, states, next_states, rewards, dones):

        adv = []
        gae = 0
        with torch.no_grad():  # adv and v_target have no gradient
            vs = self.critic(states)
            vs_ = self.critic(next_states)
            deltas = rewards + self.gamma * (1.0 - dones) * vs_ - vs
            for delta, d in zip(reversed(deltas.detach().cpu().numpy()), reversed(dones.detach().cpu().numpy())):
                gae = delta + self.gamma * self.lmbda * gae * (1.0 - d)
                adv.insert(0, gae)
            adv = torch.tensor(adv, dtype=torch.float).view(-1, 1).to(self.device)
            adv = ((adv - adv.mean()) / (adv.std() + 1e-5))  # Trick 1:advantage normalization
            v_target = adv + vs
        return adv, v_target


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
        avail_bi = [1 if x in ope else 0 for x in node]
        avail = np.array([np.repeat(1, 12) if x in ope else np.repeat(0, 12) for x in node]).reshape(1, -1)
        # mask方法，分成avail和non_avail放到actor里面去训练
        # 根据avail拆成两部分，然后每个部分走mlp,最后输出一个prob,
        # 尝试两种方式，一种是不可用动作均分概率，另外一种None单独算prob,剩下的不可用动作赋值为0.
        #梯度的传播可以参考PPO中的方法
        # dimension : 1*(Nm*Nj*12),1*(Nm*Nj*12),1*(Nm*Nj),1*(Nm*Nj)
        return state_vec, avail, avail_bi, node

    def take_action(self, state, avail, avail_bi, node, status):
        # avail, nonavail:  用于state向量的可行操作mask
        # avail_bi nonavail_bi: 用于prob向量的可行操作mask
        prob_STSP = STSP_prob(status).to(self.device)
        prob_workload = busy_balance(status).to(self.device)
        nonavail = [1 - i for i in avail]
        nonavail_bi = [1 - i for i in avail_bi]
        state_avail = torch.tensor(state * avail, dtype=torch.float).detach()
        state_nonavail = torch.tensor(state * nonavail, dtype=torch.float).detach()
        # mask方法，分成avail和non_avail放到actor里面去训练
        prob_avail = self.actor(state_avail.to(self.device)).view(-1, 1)
        prob_nonavail = self.actor(state_nonavail.to(self.device)).view(-1, 1)
        avail_bi = torch.tensor(avail_bi, dtype=torch.float).to(self.device).view(-1, 1)
        nonavail_bi = torch.tensor(nonavail_bi, dtype=torch.float).to(self.device).view(-1, 1)
        prob_avail_norm = F.normalize((prob_avail*avail_bi).clone().detach(), p=1, dim=0)
        prob_non = (prob_nonavail*(nonavail_bi)).mean(dim=0)
        '''print('STSP',prob_STSP)
        print('balance', busy_balance(status))
        print('avail',prob_avail_norm)
        print('non',prob_non)'''
        # STSP+busy balance based DRL
        prob_guidance = self.alpha1 * prob_STSP + self.alpha2 * prob_workload
        prob = prob_avail_norm+prob_non*(nonavail_bi)+prob_guidance+1e-6

        action_prob = F.normalize(prob, p=1, dim=0)
        action_dist = torch.distributions.Categorical(action_prob.squeeze())
        action_num = action_dist.sample().item()
        action_node = node[action_num]
        action = [item for item in status.available_operations if item is not None and item[0] == action_node[0] and item[1] == action_node[1]]
        action = action[0] if len(action) == 1 else None
        return prob_guidance.detach().cpu().numpy(), action, action_num, action_prob.detach().cpu().numpy()

    def update(self, replay_buffer, batch_size):
        device = self.device
        states, action_num, prob_guidance, prob, avail, avail_bi, rewards, next_states, dones = replay_buffer.sample(batch_size, device)
        # 时序差分目标
        states = states.squeeze(1)
        avail = avail.squeeze(1)
        nonavail = 1-avail
        avail_bi = avail_bi.squeeze(1)
        prob_guidance = prob_guidance.squeeze(2)
        action_probs = prob.squeeze(2)
        next_states = next_states.squeeze(1)
        rewards = F.normalize(rewards, p=2)
        td_target, advantage = self.v_target(states, next_states, rewards, dones)
        old_log_probs = torch.log(action_probs.gather(1, action_num)).detach()
        for _ in range(self.epochs):
            with torch.no_grad():
                state_avail = (states * avail)
                state_nonavail = (states * nonavail)
            prob_avail = self.actor(state_avail.to(self.device))
            prob_nonavail = self.actor(state_nonavail.to(self.device))
            prob_avail_norm = F.normalize((prob_avail * avail_bi.detach()), p=1, dim=0)
            nonavail_bi = (1-avail_bi).detach()
            prob_non = (prob_nonavail * nonavail_bi).mean(dim=0)
            prob = prob_avail_norm + prob_non * nonavail_bi + prob_guidance + 1e-6
            # prob: batch_size*(Nm*Nj)
            new_prob = F.normalize(prob, p=1, dim=1)
            log_prob = torch.log(new_prob.gather(1, action_num))
            new_probs = new_prob.unsqueeze(2).permute(0, 2, 1)
            dist = torch.distributions.Categorical(probs=new_probs)
            dist_entropy = dist.entropy().view(-1, 1)
            ratio = torch.exp(log_prob - old_log_probs)
            surr1 = ratio * advantage
            surr2 = torch.clamp(ratio, 1 - self.eps, 1 + self.eps) * advantage  # 截断
            actor_loss = -torch.min(surr1, surr2) - dist_entropy*0.01  # PPO损失函数
            critic_loss = F.mse_loss(self.critic(states), td_target.detach())
            self.actor_optimizer.zero_grad()
            self.critic_optimizer.zero_grad()
            actor_loss.mean().backward()
            critic_loss.backward()
            # Trick : Gradient clip
            torch.nn.utils.clip_grad_norm_(self.actor.parameters(), 0.5)
            torch.nn.utils.clip_grad_norm_(self.critic.parameters(), 0.5)
            self.actor_optimizer.step()
            self.critic_optimizer.step()
            self.actor_loss.append(actor_loss.mean().detach().cpu().numpy())
            self.critic_loss.append(critic_loss.mean().detach().cpu().numpy())


    def train_single(self, buffer_size=2048, minimal_buffer_size=128, batch_size=64, instance='IS3J5M5R0', episodes=500, plot_process=True):
        replay_buffer = ReplayBuffer(buffer_size)
        return_l = []
        makespan_l = []
        for i in range(10):
            with tqdm(total=int(episodes / 10), desc='Iteration %d' % i) as pbar:
                for i_episode in range(int(episodes / 10)):
                    instance_reward = 0
                    env: JSRSInstance = JSRS.make(instance)
                    status = env.reset()
                    while not status.done:
                        state, avail, avail_bi, node = self.get_state_vec(status)
                        prob_guidance, action, action_num, prob = self.take_action(state, avail, avail_bi, node, status)
                        tran_time = trantime(action)
                        next_status = env.step(action)
                        next_state = self.get_state_vec(next_status)[1]
                        reward = state_reward(status, next_status, action)-tran_time
                        if action is None:
                            reward -= 500
                        replay_buffer.add(state, action_num, prob_guidance, prob, avail, avail_bi, reward, next_state, env.done)
                        status = next_status
                        instance_reward += reward
                    if replay_buffer.size() > minimal_buffer_size:
                        self.update(replay_buffer, batch_size)
                    instance_reward = instance_reward*0.01 - env.makespan
                    return_l.append(instance_reward)
                    makespan_l.append(env.makespan)
                    if (i_episode + 1) % 10 == 0:
                        pbar.set_postfix({
                            'episode':
                                '%d' % (episodes / 10 * i + i_episode + 1),
                            'return':
                                '%.3f' % np.mean(return_l[-10:])
                        })
                        print(return_l[-10:])
                    pbar.update(1)

        if plot_process:
            plt.plot(return_l)
            plt.xlabel('Episodes')
            plt.ylabel('Average Returns')
            plt.title('PPO')
            plt.show()

            min_makespan = min(makespan_l)
            plt.plot(makespan_l)
            plt.xlabel('Episodes')
            plt.ylabel('Average Makespan')
            plt.ylim(min_makespan-50, min_makespan+300)
            plt.title('PPO (Min makespan: {})'.format(min(makespan_l)))
            plt.show()

            plt.plot(self.critic_loss)
            plt.xlabel('Episodes')
            plt.ylabel('Critic_Loss')
            plt.show()

            plt.plot(self.actor_loss)
            plt.xlabel('Episodes')
            plt.ylabel('Actor_Loss')
            plt.show()

        return return_l, makespan_l

    def train_loop(self, buffer_size=2048, minimal_buffer_size=128, batch_size=64, instance_list=None,
                   episodes=500, plot_process=True, val_process=False, val_data=None):
        replay_buffer = ReplayBuffer(buffer_size)
        return_l = []
        makespan_l = []
        instances_makespan = []
        val_final_makespan = pd.DataFrame()
        val_final_trantime = pd.DataFrame()
        #makespan_data = pd.DataFrame()
        #trantime_data = pd.DataFrame()
        num=0
        for i in range(10):
            with tqdm(total=int(episodes / 10), desc='Iteration %d' % i) as pbar:
                for i_episode in range(int(episodes / 10)):
                    episode_return, episode_makespan, episode_tran_time = [], [], []
                    for instance in instance_list:
                        instance_reward = 0
                        tran_total = 0
                        env: JSRSInstance = JSRS.make(instance, 'Data/new/' + instance + '.jsr')
                        status = env.reset()
                        action_note = []
                        trantime_note = []
                        while not status.done:
                            state, avail, avail_bi, node = self.get_state_vec(status)
                            prob_guidance, action, action_num, prob = self.take_action(state, avail, avail_bi, node, status)
                            tran_time = trantime(action)
                            next_status = env.step(action)
                            next_state = self.get_state_vec(next_status)[1]
                            reward = state_reward(status, next_status, action) - tran_time
                            if action is None:
                                reward -= 500
                            replay_buffer.add(state, action_num, prob_guidance, prob, avail, avail_bi, reward, next_state,
                                              env.done)
                            status = next_status
                            instance_reward += reward
                            tran_total += tran_time
                            action_note.append(action)
                            trantime_note.append(tran_time)
                        if replay_buffer.size() > minimal_buffer_size:
                            self.update(replay_buffer, batch_size)
                        instance_reward = instance_reward*0.01 - env.makespan
                        episode_makespan.append(env.makespan)
                        episode_return.append(instance_reward)
                        episode_tran_time.append(tran_total)
                        machine_processing_records = {machine.id: machine.logs for machine in env.machine_register.values()}

                        action_records = pd.DataFrame({'action':action_note,'trantime':trantime_note})
                    return_l.append(sum(episode_return)/len(episode_return))
                    #makespan_data[num] = episode_makespan
                    #trantime_data[num] = episode_tran_time
                    makespan_l.append(episode_makespan)
                    instance_makespan = sum(episode_makespan)/len(episode_makespan)
                    instances_makespan.append(instance_makespan)
                    num += 1
                    if (i_episode + 1) % 10 == 0:
                        pbar.set_postfix({
                            'episode':
                                '%d' % (episodes / 10 * i + i_episode + 1),
                            'return':
                                '%.3f' % np.mean(return_l[-10:]),
                            'makespan':
                                '%.3f' % np.mean(instances_makespan[-10:]),
                            'min_makespan':
                                '%.3f' % min(instances_makespan)
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
                                vstate, vavail, vavail_bi, vnode = self.get_state_vec(val_status)
                                vprob_guidance, vaction, vaction_num, vprob = self.take_action(vstate, vavail, vavail_bi, vnode,
                                                                                           val_status)
                                vtran_time = trantime(vaction)
                                val_next_status = val_env.step(vaction)
                                vtran_total += vtran_time
                                val_status = val_next_status
                            makespan_val.append(val_env.makespan)
                            trantime_val.append(vtran_total)
                        val_final_makespan[num] = makespan_val
                        val_final_trantime[num] = trantime_val
        import os
        output_dir = 'D:/记录/课程、比赛/研二/HR_based DRL in JSRS'
        if os.path.exists(output_dir):
            val_final_makespan.T.to_csv(os.path.join(output_dir, 'val_data_makespan.csv'))
            val_final_trantime.T.to_csv(os.path.join(output_dir, 'val_data_trantime.csv'))
        #trantime_data.T.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/trantime.csv')
        #makespan_data.T.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/makespan.csv')
        #print(machine_processing_records)
        #action_records.to_csv('D:/记录/课程、比赛/研二/HR_based DRL in JSRS/action_logs.csv')

        if plot_process:
            plt.plot(moving_average(return_l, 9))
            plt.xlabel('Episodes')
            plt.ylabel('Average Returns')
            plt.title('KGDRL')
            plt.show()

            min_makespan = min(instances_makespan)
            max_makespan = max(instances_makespan)
            plt.plot(moving_average(instances_makespan, 9))
            plt.xlabel('Episodes')
            plt.ylabel('Average Makespan')
            plt.ylim(min_makespan-50, max_makespan+50)
            plt.title('KGDRL (Min makespan: {})'.format(min(instances_makespan)))
            plt.show()

            '''makespan_ave = np.mean(np.array(instances_makespan).reshape(10, 100), axis=0)
            plt.plot(makespan_ave)
            plt.xlabel('Episodes')
            plt.ylabel('Average Makespan')
            plt.ylim(400, 650)
            plt.title('PPO (Min makespan: {})'.format(min(instances_makespan)))
            plt.show()'''
        return return_l, makespan_l, instances_makespan

if __name__ == '__main__':
    # 训练
    random.seed(0)
    np.random.seed(0)
    torch.manual_seed(0)

    my_dvl = PPO(hidden_dim=128, state_d=5*5*12, action_d=5*5, actor_lr=5e-4, critic_lr=1e-5)
    instance_names = ['IS{}J{}M{}R{}'.format(3, 5, 5, i) for i in range(20)]
    val_names = ['IS{}J{}M{}R{}'.format(3, 5, 5, i) for i in range(25)]
    return_list, makespan_list, instance_makespan = my_dvl.train_loop(instance_list=instance_names, episodes=500, val_process=True, val_data=val_names)
    #return_list, makespan_list = my_dvl.train_single(instance='IS3J30M10R17')
    #cmax = my_dvl.evaluate(show_status=True)









