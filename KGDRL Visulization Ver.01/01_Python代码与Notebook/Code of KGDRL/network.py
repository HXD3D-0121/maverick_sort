"""
    Author: Zhanluo Zhang
    Author E-mail: zhangzhanluo@outlook.com
    Version: v1.0
    Created Date: 2022/11/17
    Description: 定义网络结构，快速转换
"""
import torch
import networkx as nx
from torch_geometric.utils import to_networkx
from typing import List
from torch_geometric.data import Data
from matplotlib import pyplot as plt
from env import JSRS, JSRSStatus, Stage

BIG_NUMBER = 1e6


def show_graph(graph):
    graph_nx = to_networkx(graph)
    nx.draw(graph_nx, with_labels=True, font_color='white')
    plt.show()


def get_unfinished_stages(job) -> List[Stage]:
    if job.current_stage is None:
        return job.stages
    else:
        current_stage_id = job.stages.index(job.current_stage)
        return job.stages[current_stage_id:]


def update_edge_info(edge_types, edge_list, edge_attr, source_node, dest_node, edge_type=None):
    assert edge_type in edge_types
    edge = (source_node, dest_node)
    if edge in edge_list:
        edge_idx = edge_list.index(edge)
        edge_attr[edge_idx][edge_types.index(edge_type)] = 1
    else:
        edge_list.append(edge)
        edge_attr.append([0, 0, 0])
        edge_attr[-1][edge_types.index(edge_type)] = 1


def to_network(instance_status: JSRSStatus):
    node_id = 0
    node_types = ['processing', 'waiting', 'available', 'unavailable', 'future']
    """
    processing: 正在加工
    waiting：正在等待，指任务正在排队
    available：可用节点，使之未来的可行节点
    unavailable：因为设备不在对应的阶段因而不可用
    future：设备正在切换，过段时间就可以用了
    """
    node_features = []
    edge_types = ['task', 'machine', 'stage']
    edge_list = []
    edge_attr = []
    machine_nodes = {machine: [] for machine in instance_status.machine_register.values()}
    for job_id, job in instance_status.job_register.items():
        if len(job.stages) == 0:
            continue
        last_stage_nodes = []
        for stage in get_unfinished_stages(job):
            current_stage_nodes = []
            for machine in stage.all_machines:
                # 添加节点特征
                if machine.current_task == job:
                    node_type = 'processing'
                    t = machine.next_finishing_time - instance_status.clock
                elif machine.current_task == stage:
                    node_type = 'future'
                    t = machine.next_finishing_time - instance_status.clock
                elif machine.current_stage == stage:
                    if job in stage.queue:
                        node_type = 'waiting'
                        t = BIG_NUMBER
                    else:
                        node_type = 'available'
                        t = BIG_NUMBER
                else:
                    node_type = 'unavailable'
                    t = BIG_NUMBER
                node_feature = [0 for _ in range(len(node_types))]
                node_feature[node_types.index(node_type)] = 1
                node_feature.append(t)
                node_features.append(node_feature)
                # 记录节点以外的信息
                machine_nodes[machine].append(node_id)
                current_stage_nodes.append(node_id)
                node_id += 1
            # 添加阶段边，同一阶段的节点之间，双向
            for i in range(len(current_stage_nodes)-1):
                for j in range(i+1, len(current_stage_nodes)):
                    update_edge_info(edge_types, edge_list, edge_attr,
                                     current_stage_nodes[i], current_stage_nodes[j], 'stage')
                    update_edge_info(edge_types, edge_list, edge_attr,
                                     current_stage_nodes[j], current_stage_nodes[i], 'stage')
            # 添加任务边，由同一任务的上个阶段指向下个阶段
            for last_stage_node in last_stage_nodes:
                for current_stage_node in current_stage_nodes:
                    update_edge_info(edge_types, edge_list, edge_attr,
                                     last_stage_node, current_stage_node, 'task')
            last_stage_nodes = current_stage_nodes
    # 添加机器边，同一机器的节点，双向
    for m_nodes in machine_nodes.values():
        for i in range(len(m_nodes)-1):
            for j in range(i+1, len(m_nodes)):
                update_edge_info(edge_types, edge_list, edge_attr,
                                 m_nodes[i], m_nodes[j], 'machine')
                update_edge_info(edge_types, edge_list, edge_attr,
                                 m_nodes[j], m_nodes[i], 'machine')
    edge_index = torch.tensor(edge_list, dtype=torch.long).T
    return Data(x=torch.tensor(node_features, dtype=torch.float), edge_index=edge_index,
                edge_attr=torch.tensor(edge_attr, dtype=torch.float))


if __name__ == '__main__':
    env = JSRS.make()
    status = env.reset()
    init_graph = to_network(status)
    status = env.step(status.available_operations[-2], show_status=True)
    graph_0 = to_network(status)
    show_graph(graph_0)
    status = env.step(status.available_operations[-2], show_status=True)
    status = env.step(status.available_operations[-2], show_status=True)
    status = env.step(status.available_operations[-2], show_status=True)
    graph_1 = to_network(status)
    show_graph(graph_1)
