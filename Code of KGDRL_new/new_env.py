import math
import pandas
import random
from typing import Dict, List, Tuple, Union, NoReturn


class Job:
    JOB_WAITING = 'waiting'
    JOB_PROCESSING = 'processing'
    JOB_FINISHING = 'finishing'

    def __init__(self, job_id, t_max=None, c_max=None):
        self.id = job_id
        self.stages: List[Stage] = []
        self.current_stage = None
        self.status = Job.JOB_WAITING
        self.average_processing_time: Dict[Stage, float] = dict()
        self.available_time = 0

    def __repr__(self):
        return self.id




class Stage:
    """Job Type"""

    def __init__(self, stage_id: str):
        self.id = stage_id
        self.queue: List[Job] = []
        self.all_machines: List[Machine] = []
        self.available_machines: List[Machine] = []
        self.all_jobs: List[Job] = []
        self.unscheduled_jobs: List[Job] = []

    def __repr__(self):
        return self.id

    def add_to_queue(self, job: Job, clock: float) -> NoReturn:
        self.queue.append(job)
        job.available_time = clock
        job.current_stage = self
        job.status = Job.JOB_WAITING


class Machine:
    """Machine class. Machine-centric implementation."""

    def __init__(self, machine_id: str):
        self.id = machine_id
        self.stages: List[Stage] = []
        self.speed: Dict[Stage, float] = dict()#
        self.stage_setup_time: Dict[str, float] = dict()
        self.current_stage: Stage = Stage('None')
        self.available_stage: Stage = Stage('None')
        self.current_task = None
        self.next_finishing_time = math.inf
        self.idle_time = 0  # finishing job for last job
        self.logs: List[list] = []

    def __repr__(self):
        return self.id

    def get_processing_time(self, task):
        stage = self.current_stage
        job: Job = task
        job.current_stage = job.stages[0]
        next_stage: Stage = job.current_stage
        processing_time = self.stage_setup_time['{}-{}'.format(stage.id, next_stage.id)] + \
                          job.average_processing_time[next_stage] * self.speed[next_stage]
        return processing_time

    def get_adjacent_matrix(self, job_title):
        matrix = []
        stage = self.current_stage
        job: Job = job_title
        for stage_name in job.average_processing_time.keys():
            next_stage: Stage = stage_name
            try:
                matrix.append(self.stage_setup_time['{}-{}'.format(stage.id, next_stage.id)] +
                              job.average_processing_time[next_stage] * self.speed[next_stage])
            except:
                matrix.append(10000)
        return matrix



    def start_task(self, task: Job, clock: float) -> NoReturn:
        self.current_task = task
        processing_time = self.get_processing_time(task)
        self.next_finishing_time = round(clock + processing_time, 2)
        job: Job = task
        job.status = Job.JOB_PROCESSING
        job.current_stage = job.stages[0]
        job.stages.pop(0)
        next_stage: Stage = job.current_stage
        self.current_stage.available_machines.remove(self)
        next_stage.queue.remove(job)
        next_stage.available_machines.append(self)
        self.current_stage = next_stage

        self.logs.append([task.id, clock])

    def finish_task(self, clock: float) -> NoReturn:
        if isinstance(self.current_task, Job):
            job: Job = self.current_task
            if len(job.stages) == 0:
                job.status = Job.JOB_FINISHING
                job.current_stage = None
            else:
                job.stages[0].add_to_queue(job, clock)
                job.status = Job.JOB_WAITING
                job.current_stage = job.stages[0]
        self.current_task = None
        self.next_finishing_time = math.inf
        self.idle_time = clock
        self.logs[-1].append(clock)


# 在代码中，JSRS 是一个类，用于表示该问题的实例化和解决过程。它包含了以下主要功能：

# 实例创建：通过 JSRSInstance 类加载数据文件，初始化作业、阶段和机器的状态。
# 状态管理：通过 JSRSStatus 类记录当前系统的状态，包括作业、机器、阶段的分配情况，以及可用操作等。
# 调度逻辑：实现了调度算法的核心逻辑，如查找可用操作、处理任务完成事件、更新系统状态等。
# 结果输出：支持将调度结果保存到文件中，便于分析和评估。
class JSRSStatus:
    def __init__(self, instance_name: str,
                 job_register: Dict[str, Job],
                 machine_register: Dict[str, Machine],
                 stage_register: Dict[str, Stage],
                 available_operations: List[Tuple[Machine, Union[Job, Stage]]],
                 clock: int,
                 done: bool,
                 newly_finished_operations: List[tuple],
                 newly_created: bool,
                 operation_records: list):
        self.instance_name = instance_name
        self.job_register = job_register
        self.machine_register = machine_register
        self.stage_register = stage_register
        self.available_operations = available_operations
        self.clock = clock
        self.done = done
        self.newly_finished_operations = newly_finished_operations
        self.newly_created = newly_created
        self.operation_records = operation_records

class JSRSInstance:
    def __init__(self, name, data_path):
        self.name = name
        self.data_path = data_path  # 'Data/new/' + name + '.jsr'
        """Instance data."""
        self.clock = 0
        """Time."""
        self.makespan = 0
        self.done = False
        self.newly_finished_operations = None
        self.job_register: Dict[str, Job] = {}
        self.machine_register: Dict[str, Machine] = {}
        self.stage_register: Dict[str, Stage] = {}
        self._create()
        self.operation_records = []

    def __repr__(self):
        return self.name

    def _create(self):
        with open(self.data_path, 'r') as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines]
        lines = [line.split(',') for line in lines]
        # overall info
        n_stages, n_jobs, n_machines = int(lines[1][0]), int(lines[1][1]), int(lines[1][2])
        for i in range(n_stages):
            stage_id = 'S{}'.format(i + 1)
            self.stage_register[stage_id] = Stage(stage_id)
        for i in range(n_jobs):
            job_id = 'J{}'.format(i + 1)
            self.job_register[job_id] = Job(job_id)
        for i in range(n_machines):
            machine_id = 'M{}'.format(i + 1)
            self.machine_register[machine_id] = Machine(machine_id)
        # job info
        line_pointer = 2
        for i in range(1, n_jobs + 1):
            line = lines[line_pointer + i]
            job_id = line[0]
            job = self.job_register[job_id]
            job.available_time = float(line[1])
            for j in range(int((len(line) - 2) / 2)):
                job.average_processing_time[self.stage_register[line[j * 2 + 2]]] = float(
                    line[j * 2 + 3])
            job.stages = list(job.average_processing_time.keys())
            for stage in job.stages:
                stage.all_jobs.append(job)
                stage.unscheduled_jobs.append(job)
        # machine info
        line_pointer = line_pointer + n_jobs + 1
        for i in range(1, n_machines + 1):
            line = lines[line_pointer + i]
            machine_id = line[0]
            machine = self.machine_register[machine_id]
            machine.current_stage = self.stage_register[line[1]]
            self.stage_register[line[1]].available_machines.append(machine)
            for j in range(int((len(line) - 1) / 2)):
                machine.speed[self.stage_register[line[j * 2 + 2]]] = float(line[j * 2 + 3])
            machine.stages = list(machine.speed.keys())
            for stage in machine.stages:
                stage.all_machines.append(machine)
        # reconfiguration info
        line_pointer = line_pointer + n_machines + 1
        for i in range(n_machines):
            machine_start_line = lines[line_pointer + 1]
            machine_id = machine_start_line[0]
            for j in range(len(machine_start_line) - 1):
                for k in range(1, len(machine_start_line)):
                    start_stage_id = lines[line_pointer + 2 + j][0]
                    end_stage_id = lines[line_pointer + 1][k]
                    self.machine_register[machine_id].stage_setup_time[
                        '{}-{}'.format(start_stage_id, end_stage_id)] = float(lines[line_pointer + 2 + j][k])
            line_pointer += len(self.machine_register[machine_id].stages) + 1
        #initial scheduling
        for job in self.job_register.values():
            if job.available_time <= self.clock:
                job.stages[0].queue.append(job)

    def find_available_operations(self, add_none=True):
        """Find available operations. Return the operation ids instead of operation."""
        avails = []
        for stage in self.stage_register.values():
            for machine in stage.all_machines:
                if machine.current_task is None:
                    for job in stage.queue:
                        avails.append((machine, job, stage))
                    '''
                    for other_stage in machine.stages:
                        if other_stage != stage:
                            available_operations.append((machine, other_stage))
                    '''
        if add_none:
            if len(avails) == 0:
                avails.append(None)
        available_operations = []
        for ope in avails:
            if ope not in available_operations:
                available_operations.append(ope)

        return available_operations

    def status(self, newly_created=False, add_none=True):
        """return the detail of the system."""
        self.check_done()
        return JSRSStatus(instance_name=self.name,
                          job_register=self.job_register,
                          machine_register=self.machine_register,
                          stage_register=self.stage_register,
                          available_operations=self.find_available_operations(add_none),
                          clock=self.clock,
                          done=self.done,
                          newly_finished_operations=[] if self.newly_finished_operations is None
                          else self.newly_finished_operations,
                          newly_created=newly_created,
                          operation_records=self.operation_records)

    @staticmethod
    def show_status(s):
        print('\n' + '=' * 120)
        print('Clock:', s.clock)
        print('Newly finished operations:', s.newly_finished_operations)
        for stage in s.stage_register.values():
            print(stage.id, end='\t')
            machine_info = [(machine.id, machine.current_task) for machine in stage.all_machines]
            print(machine_info, end='\t')
            print(stage.queue)
        print('Available operations:', s.available_operations)
        print('=' * 120)

    def reset(self, show_status=False) -> JSRSStatus:
        """Reset the environment. Return (observations, clock, done, info)."""
        self.__init__(self.name, self.data_path)
        #self._init_scheduling()
        status_return = self.status(newly_created=True)
        self.operation_records = []
        if show_status:
            self.show_status(status_return)
        return status_return

    def process_to_next_event(self):
        """
        所有机器的下一完成时间最小的为下个时刻。如果所有机器都空闲，意味着不会存在下一时刻，返回的是空集合，
        否则使系统切换到下一时刻，并进行相应的处理。

        :return: 新完工的操作
        """
        newly_finished_operations = []
        next_decision_moment = min([machine.next_finishing_time for machine in self.machine_register.values()])
        if next_decision_moment == math.inf:  # no new event, all machine are idle
            return newly_finished_operations
        next_machines = [machine for machine in self.machine_register.values() if
                         machine.next_finishing_time == next_decision_moment]
        self.clock = next_decision_moment
        for next_machine in next_machines:
            newly_finished_operations.append((next_machine, next_machine.current_task))
            next_machine.finish_task(self.clock)
        return newly_finished_operations

    def check_done(self):
        if all([len(job.stages) == 0 for job in self.job_register.values()]):
            self.done = True
            # check the last finishing job for the makespan
            if len([machine.next_finishing_time for machine in self.machine_register.values()
                    if machine.current_task is not None and isinstance(machine.current_task, Job)]) == 0:
                pass
            self.makespan = max([machine.next_finishing_time for machine in self.machine_register.values()
                                 if machine.current_task is not None and isinstance(machine.current_task, Job)])
            return True
        else:
            return False

    def step(self, operation: Union[None, Tuple[Machine, Job, Stage]], show_status=False) -> JSRSStatus:
        self.newly_finished_operations = None
        self.operation_records.append((operation, self.clock))
        # Process selected action
        if operation is None:
            self.newly_finished_operations = self.process_to_next_event()
            if len(self.newly_finished_operations) == 0:  # no new event, you can not choose to do nothing
                status_return = self.status(add_none=False)
                if show_status:
                    self.show_status(status_return)
                return status_return
            else:
                status_return = self.status(add_none=True)
                if show_status:
                    self.show_status(status_return)
                return status_return
        else:
            stage: Stage = operation[2]
            schedule_job: Job = operation[1]
            stage.unscheduled_jobs = [x for x in stage.unscheduled_jobs if x != schedule_job]
        available_operations = self.find_available_operations()
        if operation not in available_operations:
            raise NameError('The provided operation {} id is wrong.'.format(str(operation)))
        operation[0].start_task(operation[1], self.clock)

        # What to do next. There must be some operations to be processed.
        if not self.check_done():
            ready_machines = [machine for machine in self.machine_register.values() if
                              machine.current_task is None and len(machine.stages) > 1]
            self.newly_finished_operations = []
            while len(ready_machines) == 0:
                next_finished_operations = self.process_to_next_event()
                self.newly_finished_operations.extend(next_finished_operations)
                ready_machines = [machine for machine in self.machine_register.values() if
                                  machine.current_task is None and len(machine.stages) > 1]
        status_return = self.status()
        if show_status:
            self.show_status(status_return)
        return status_return

    def output_text_result(self, method='unknown_method'):
        """Result saved to 'Data/Results/{} {} {}.txt'.format(self.name, self.clock, method)"""
        result_file = 'Data/Results/{} {} {}.txt'.format(self.name, self.clock, method)
        with open(result_file, 'w') as f:
            for machine_id, machine in self.machine_register.items():
                f.write(str(machine_id) + ': ')
                for i, log in enumerate(machine.logs):
                    f.write(str(log))
                    if i < len(machine.logs) - 1:
                        f.write(',')
                    else:
                        f.write('\n')


class JSRS:
    """Job shop reconfiguration scheduling problem instance."""

    def __int__(self):
        pass

    @staticmethod
    def make(instance_name='example', data_path='Data/new/' + 'IS3J5M5R3' + '.jsr'):
        instance = JSRSInstance(instance_name, data_path)
        return instance


if __name__ == '__main__':
    random.seed(0)
    env = JSRS.make('IS3J5M5R3','Data/new/' + 'IS3J5M5R3' + '.jsr')
    status = env.reset(show_status=True)
    while not status.done:
        action = random.choice(status.available_operations)
        status = env.step(action, show_status=True)
    env.output_text_result()



