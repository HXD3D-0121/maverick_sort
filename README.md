# Job Shop Reconfiguration Scheduling Problem (JSRS, 可重新配置的任务车间调度问题)

#### About reconfiguration for rules
- The machine is allowed to be reconfigured only when the machine is idle and 
there are no waiting jobs in the current stage and 
some waiting jobs in the target stage;
- We do not consider predicting possible jobs in the near future, meaning once it can be reconfigured, we will do it.

#### Operations
##### Code form
Union[None, Tuple[Machine, Union[Job, Stage]]]
##### explanation
If a machine is idle, then there are operations available. 
The operations can be starting a new job and configuring the machine into another stage.
In some cases, if there are no waiting jobs in the target stage, there reconfiguration operation is illegal (See above).
The operation can also be None, meaning doing nothing and wait for the next decision moment. 
(See [this pic](Pics/Explain%20None%20Operation.png) for a None case)
Generally, you can see a None everytime you need to do a decision. 
If you do not see it, it is because you choose None last time. 
However, we can not find next decision moment since all machines are idle.

## RL
#### State
- info of current operation
  - processing time
  - 
- info of all jobs
  - 
- info of all machines
- info of all stages
#### Action