import torch
import random
import torch.nn.functional as F
import math
from new_env import Job, Machine, JSRS, JSRSInstance, JSRSStatus, Stage
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
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

def compute_advantage(gamma, lmbda, td_delta):
    td_delta = td_delta.detach().numpy()
    advantage_list = []
    advantage = 0.0
    for delta in td_delta[::-1]:
        advantage = gamma * lmbda * advantage + delta
        advantage_list.append(advantage)
    advantage_list.reverse()
    return torch.tensor(advantage_list, dtype=torch.float)

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
        #F.softmax(self.fc4(x), dim=1)
            #log_softmax(self.fc2(x), dim=1)




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
    def __init__(self, hidden_dim=None, state_d=5, action_d=5, actor_lr=5e-6, critic_lr=1e-8, gamma=0.96,
                 lmbda=0.95, epochs=30, eps=0.1):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        print('Device: ', self.device)
        # state由ma和job特征向量embedding而成
        state_dim = state_d
        hidden_dim = state_dim * 5 if hidden_dim is None else hidden_dim
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

    def v_target(self, states, next_states, rewards, dones):

        """
        Calculate the advantage using GAE
        'dw=True' means dead or win, there is no next state s'
        'done=True' represents the terminal of an episode(dead or win or reaching the max_episode_steps). When calculating the adv, if done=True, gae=0
        """
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
        probs = probs * avail+1e-6
        action_probs = F.normalize(probs, p=1, dim=0)
        action_dist = torch.distributions.Categorical(action_probs.squeeze())
        action_num = action_dist.sample().item()
        action_node = operation[action_num]
        action = [item for item in status.available_operations if
                  item is not None and item[0] == action_node[0] and item[1] == action_node[1]]
        action = action[0] if len(action) == 1 else None
        old_probs = np.array(action_probs.detach().cpu().numpy()).reshape(1, -1)
        #把none_action的概率均匀离散到所有不可用的动作上面，形成一个Ns*Nm*Nj的张量
        return action, action_num, old_probs, avail.detach().cpu().numpy()


    def update(self, transition_dict):
        # state dimension : (n*(Nm*No)*6)
        states = torch.tensor(transition_dict['states_vec'],
                              dtype=torch.float).to(self.device)
        action_num = torch.tensor(transition_dict['action_num'],
                                  dtype=torch.int64).view(-1, 1).to(self.device)
        action_probs = torch.tensor(transition_dict['action_probs'],
                                    dtype=torch.float).to(self.device)
        avail = torch.tensor(transition_dict['avail'],
                             dtype=torch.float).to(self.device)
        rewards = torch.tensor(transition_dict['rewards'],
                               dtype=torch.float).view(-1, 1).to(self.device)
        next_states = torch.tensor(transition_dict['next_states'],
                                   dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict['dones'],
                             dtype=torch.float).view(-1, 1).to(self.device)

        # 时序差分目标
        states = states.squeeze(1)
        action_probs = action_probs.squeeze(1)
        avail = avail.squeeze(2)
        next_states = next_states.squeeze(1)
        rewards = F.normalize(rewards, p=2, dim=0)
        td_target, advantage = self.v_target(states, next_states, rewards, dones)
        old_log_probs = torch.log(action_probs.gather(1, action_num)).detach()
        for _ in range(self.epochs):
            #print('loop start')
            new_probs = self.actor(states)
            new_probs_shaped = new_probs*avail+1e-6
            #通过矩阵运算把prob修改成最后的结果
            new_soft_prob = F.normalize(new_probs_shaped, p=1, dim=0)
            log_probs = torch.log(new_soft_prob.gather(1, action_num))
            new_probs_s = new_soft_prob.unsqueeze(2).permute(0, 2, 1)
            dist = torch.distributions.Categorical(probs=new_probs_s)
            dist_entropy = dist.entropy().view(-1, 1)
            ratio = torch.exp(log_probs - old_log_probs)
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


    def train_loop(self, instance_list, episodes=200, plot_process=False):
        return_l = []
        makespan_l = []
        instances_makespan = []
        for i in range(10):
            with tqdm(total=int(episodes / 10), desc='Iteration %d' % i) as pbar:
                for i_episode in range(int(episodes / 10)):
                    episode_return, episode_makespan = [], []
                    transition_dict = {
                        'states_vec': [],
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
                            transition_dict['states_vec'].append(states_vec)
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
            plt.title('A2C')
            plt.show()

            min_makespan = min(instances_makespan)
            plt.plot(instances_makespan)
            plt.xlabel('Episodes')
            plt.ylabel('Average Makespan')
            plt.ylim(min_makespan-50, min_makespan+300)
            plt.title('A2C (Min makespan: {})'.format(min(instances_makespan)))
            plt.show()

        return return_l, makespan_l, instances_makespan



if __name__ == '__main__':
    # 训练
    random.seed(0)
    np.random.seed(0)
    torch.manual_seed(0)

    my_dvl = PPO(hidden_dim=128, state_d=10*5*12, action_d=10*5, actor_lr=5e-4, critic_lr=1e-5)
    instance_names = ['IS{}J{}M{}R{}'.format(3, 10, 5, i+10) for i in range(10)]
    return_list, makespan_list, instance_makespan = my_dvl.train_loop(instance_list=instance_names, episodes=100)
    #cmax = my_dvl.evaluate(show_status=True)

