import random
#这段代码的目的是生成一个调度问题的随机实例

def define_instance_name(n_stages, n_jobs, n_machines, random_seed):
    return 'IS{}J{}M{}R{}'.format(n_stages, n_jobs, n_machines, random_seed)


def instance_design(s, j, m):
    instance_item = [(s, j, m, i+10) for i in range(10)]
    return instance_item


def create_instance(folder='Data/new/', instance=None,
                    processing_time_mean=100,
                    processing_time_cv=0.3,
                    setup_time_mean=10,
                    setup_time_cv=0.1,
                    random_arriving_time=False):
    n_stages = instance[0]
    n_jobs = instance[1]
    n_machines = instance[2]
    random_seed = instance[3]
    instance_name = define_instance_name(n_stages, n_jobs, n_machines, random_seed)
    file_name = folder + instance_name + '.jsr'
    random.seed(random_seed)
    stage_names = ['S{}'.format(i + 1) for i in range(n_stages)]
    job_names = ['J{}'.format(i + 1) for i in range(n_jobs)]
    machine_names = ['M{}'.format(i + 1) for i in range(n_machines)]
    job_stage_names = [sorted(random.sample(stage_names, k=n_stages)) for _ in range(n_jobs)]
    machine_stage_names = [sorted(random.sample(stage_names, k=random.randint(1, n_stages))) for _ in range(n_machines)]
    all_job_stage_names = set(sum(job_stage_names, []))
    all_machine_stage_names = set(sum(machine_stage_names, []))
    job_stage_names[0].extend(list(set(stage_names) - all_job_stage_names))
    machine_stage_names[0].extend(list(set(stage_names) - all_machine_stage_names))
    arriving_times = [random.randint(0, 1000) if random_arriving_time else 0 for _ in range(n_jobs)]
    with open(file_name, 'w') as f:
        f.write('<overall info: n_stages, n_jobs, n_machines>\n')
        f.write(','.join([str(n_stages), str(n_jobs), str(n_machines)]))
        f.write('\n')
        f.write('<job info: arriving_time and average_processing_time>\n')
        for i, job_name in enumerate(job_names):
            f.write(job_name + ',' + str(arriving_times[i]))
            for stage_name in job_stage_names[i]:
                f.write(',' + stage_name + ',')
                f.write(str(max(1,
                                int(random.normalvariate(mu=processing_time_mean,
                                                         sigma=processing_time_mean * processing_time_cv)))))
            f.write('\n')
        f.write('<machine info: initial_stage and speed>\n')
        for i, machine_name in enumerate(machine_names):
            f.write(machine_name + ',' + random.choice(machine_stage_names[i]))
            for stage_name in machine_stage_names[i]:
                f.write(',' + stage_name + ',')
                f.write(str(round(random.randint(1, 19) * 0.1, 1)))
            f.write('\n')
        f.write('<reconfiguration info: setup_time>\n')
        for i, machine_name in enumerate(machine_names):
            f.write(machine_name + ',')
            f.write(','.join(machine_stage_names[i]))
            f.write('\n')
            for j, stage_name in enumerate(machine_stage_names[i]):
                f.write(stage_name)
                for k in range(len(machine_stage_names[i])):
                    f.write(',')
                    if j == k:
                        f.write('0')
                    else:
                        f.write(str(max(1, int(random.normalvariate(mu=setup_time_mean,
                                                                    sigma=setup_time_mean * setup_time_cv)))))
                f.write('\n')
        f.write('<end>')
    random.seed(None)
    return instance_name


if __name__ == '__main__':
    instance_designed = instance_design(s=3, j=50, m=5)
    for instance_case in instance_designed:
        create_instance(instance=instance_case)