import gymnasium as gym
import math
from gymnasium import spaces
import numpy as np
import random

Train0 = []
Train1 = []
Train2 = []
for i in range (200):
  Train0.append(random.randint(1, 100))
  Train1.append(random.randint(1, 100))
  Train2.append(random.randint(1, 100))

Train0 = [56, 24, 41, 51, 61, 26, 9, 60, 13, 37, 9, 52, 86, 93, 73, 31, 57, 26, 68, 71, 39, 46, 34, 99, 61, 83, 23, 15, 21, 75, 46, 60, 56, 64, 31, 68, 41, 71, 95, 59, 100, 61, 65, 68, 16, 7, 40, 21, 52, 20, 2, 85, 25, 89, 39, 64, 78, 20, 11, 55, 48, 87, 78, 62, 76, 69, 22, 60, 67, 13, 50, 35, 86, 97, 68, 59, 12, 64, 75, 25, 35, 87, 91, 41, 45, 39, 73, 55, 96, 83, 58, 99, 33, 12, 61, 89, 74, 62, 32, 98, 12, 93, 23, 56, 54, 47, 76, 41, 22, 84, 19, 25, 10, 53, 47, 29, 38, 97, 25, 61, 25, 60, 60, 77, 27, 16, 33, 90, 14, 72, 76, 85, 90, 49, 47, 93, 11, 45, 88, 30, 44, 53, 31, 97, 96, 15, 46, 79, 14, 74, 54, 94, 97, 33, 84, 45, 78, 24, 96, 84, 68, 89, 32, 4, 35, 46, 19, 12, 99, 69, 36, 63, 95, 19, 95, 77, 61, 1, 82, 90, 24, 12, 41, 42, 100, 65, 52, 42, 99, 7, 5, 71, 18, 27, 91, 87, 57, 70, 39, 20]
Train1 = [36, 46, 81, 54, 28, 6, 25, 42, 77, 27, 87, 16, 26, 27, 55, 47, 31, 20, 54, 3, 93, 53, 10, 94, 40, 15, 35, 73, 55, 97, 82, 7, 44, 60, 90, 39, 73, 53, 64, 48, 46, 11, 23, 61, 96, 39, 54, 41, 62, 40, 14, 11, 6, 64, 91, 84, 26, 95, 46, 50, 17, 84, 81, 82, 33, 53, 60, 3, 48, 26, 89, 51, 75, 48, 55, 60, 63, 15, 26, 17, 23, 82, 97, 51, 38, 90, 69, 81, 75, 89, 85, 69, 43, 53, 99, 54, 12, 32, 40, 69, 21, 3, 61, 52, 87, 54, 95, 52, 21, 52, 26, 44, 19, 76, 33, 68, 85, 25, 86, 20, 92, 73, 50, 92, 38, 36, 44, 35, 79, 16, 59, 85, 99, 67, 68, 87, 9, 18, 16, 47, 10, 49, 35, 66, 66, 5, 52, 89, 21, 89, 37, 99, 83, 10, 48, 70, 91, 50, 23, 25, 50, 43, 86, 59, 73, 57, 86, 2, 12, 84, 25, 80, 44, 14, 51, 60, 8, 73, 33, 20, 21, 42, 72, 57, 95, 2, 24, 64, 26, 18, 68, 26, 36, 92, 58, 78, 76, 69, 79, 76]
Train2 = [1, 76, 45, 51, 6, 26, 23, 38, 30, 40, 92, 67, 36, 66, 51, 100, 20, 27, 73, 76, 97, 30, 1, 55, 53, 45, 14, 9, 97, 2, 66, 50, 39, 95, 84, 13, 85, 86, 50, 6, 39, 71, 89, 34, 40, 8, 100, 73, 100, 6, 76, 69, 98, 44, 18, 76, 27, 10, 94, 33, 22, 2, 2, 36, 61, 1, 67, 44, 30, 99, 5, 86, 30, 47, 60, 100, 91, 73, 9, 43, 79, 40, 71, 33, 60, 48, 83, 67, 81, 66, 83, 32, 42, 36, 39, 35, 44, 85, 64, 68, 71, 85, 37, 31, 57, 19, 33, 27, 28, 92, 75, 28, 95, 31, 44, 79, 45, 20, 54, 22, 56, 31, 7, 97, 5, 39, 39, 74, 63, 86, 58, 10, 3, 34, 70, 37, 43, 82, 100, 90, 37, 84, 22, 87, 30, 36, 22, 84, 72, 32, 60, 47, 17, 46, 63, 28, 33, 80, 37, 94, 45, 15, 44, 83, 63, 6, 62, 14, 16, 67, 83, 72, 63, 42, 77, 10, 2, 16, 46, 25, 17, 75, 32, 14, 70, 56, 85, 29, 24, 82, 91, 2, 51, 8, 30, 47, 37, 30, 51, 28]

Train0 = [19, 16, 25, 47, 33, 15, 19, 13, 25, 50, 40, 66, 33, 55, 80, 33, 41, 22, 16, 18, 11, 8, 15, 9, 13, 8, 11, 8, 14, 11, 11, 19, 28, 70, 30, 27, 78, 55, 47, 44, 33, 34, 50, 66, 66, 69, 94, 53, 56, 86, 100, 56, 50, 69, 33, 25, 28, 55, 25, 17, 14, 18, 22, 12, 8, 9, 11, 8, 17, 15, 34, 28]
Train1 = [36, 41, 33, 40, 35, 42, 31, 23, 25, 15, 17, 14, 16, 8, 12, 8, 12, 10, 11, 13, 11, 21, 15, 16, 12, 18, 19, 16, 25, 47, 33, 15, 19, 13, 25, 50, 40, 66, 35, 55, 80, 33, 41, 22, 16, 18, 11, 8, 15, 9, 13, 8, 11, 8, 14, 11, 11, 19, 28, 70, 30, 27, 78, 55, 47, 44, 33, 34, 50, 66, 66, 69]
Train2 = [94, 53, 56, 86, 100, 56, 50, 69, 33, 25, 28, 55, 25, 17, 14, 18, 22, 12, 8, 9, 11, 8, 17, 15, 34, 28, 36, 41, 33, 40, 35, 42, 31, 23, 25, 15, 17, 14, 16, 8, 12, 8, 12, 10, 11, 13, 11, 21, 15, 16, 12, 18, 19, 16, 25, 47, 33, 15, 19, 13, 25, 50, 40, 66, 35, 55, 80, 33, 41, 22, 16, 18]

Train0 = [19, 28, 70, 30, 27, 78, 55, 47, 44, 33, 34, 50, 66, 66, 69, 94, 53, 56, 86, 100]
Train1 = [15, 19, 13, 25, 50, 40, 66, 35, 55, 80, 33, 41, 22, 16, 18, 11, 8, 15, 9, 13]
Train2 = [33, 34, 50, 66, 66, 69, 94, 53, 56, 86, 100, 56, 50, 69, 33, 25, 28, 55, 25, 17]
print(len(Train0), len(Train1),len(Train2))

class ParallelServiceSLO(gym.Env):
    """
    Description:
        Based on current
        - Each service's claimed resources allocation
        - Each service's response latency
        - Each service's next time step predicted traffic

        RL Agent provides a scaling configuration for all parallel services that can
        ** Satisfy all services' SLO Latency
        ** Minimize the SUM of Latency of all services

    Observation: (consider 3 parallel services)
        - Fixed Parameter:

        * Namespace Total Resource
        * Service0 Latency SLO
        * Service1 Latency SLO
        * Service2 Latency SLO


        - Type: Box(3,3)

        Index   0                              1                              2
        0       Service0 Claimed Resources     Service0 Current Latency       Service0 Next Predicted Traffic
        1       Service1 Claimed Resources     Service1 Current Latency       Service1 Next Predicted Traffic
        2       Service2 Claimed Resources     Service2 Current Latency       Service2 Next Predicted Traffic

        - State Value Range:

        Type                 Min       Max       Note
        Claimed Resources    0         100       Percentage over the fixed resources that was assigned for namespace
        Current Latency      0         100       Percentage over the Latency SLO of each service (>100% = violation)
        Predicted Traffic    0         Top*      Top = Highest traffic record in the historical traffic database

    Actions:
        - Type: MultiDiscrete([MaxS0, MaxS1, MaxS2])

        Index      0                          1                           2
        0          Service0_Scaling_Config    Service1_Scaling_Config     Service2_Scaling_Config

        - Action Value Range:

        Scaling_Config_of    Min       Max         Note
        Service0             0         1+MaxS0     MaxS0: Total possible AssignedResource-Concurrency Pair of Service0
        Service1             0         1+MaxS1     MaxS1: Total possible AssignedResource-Concurrency Pair of Service1
        Service2             0         1+MaxS2     MaxS2: Total possible AssignedResource-Concurrency Pair of Service2

        - How to find MaxS0, MaxS1, MaxS2?

        * Each service has a AssignedResource range [MinResource,MaxResource] (Min = Minimum to run service, Max = Saturated resource level, increasing more level will not increase service performance)
        * Each AssignedResource Level has a maximum Concurrency that can still guarantee service's Latency SLO
        * --> Each AssignedResource Level has a range of possible Concurrency configuration from 0 to MaxConcurrency [0, MaxConcurrency]. Split this range by a step of 10
        * --> MaxSn = Number of different AssignedResource Level * Number of different Concurrency Level per each AssignedResourceLevel

        * Example Service0: AssignedResource range [1000mCPU, 2500mCPU], Possible Actions: 7 --> MaxS0 = 7

        Index    CPU_Level     Concurrency_Level
        0        1000          10       (5  Max) (larger concurrency = SLO violation)
        1        1500          10       (10 Max)
        2,3      2000          10,20    (20 Max)
        4,5,6    2500          10,20,30 (30 Max)

        - Agent need to pre-calculated total expected resources usage for future traffic from all services,
        if Expected > Namespace Resource, remove that action from possible actions from the action space
        if no action available, action AllZero 0-0-0 will be chosen, which tell the system to redirect the request


    Reward:

        Reward = 1 / Sum of all Service Latency

        Reward =  VeryHigh for AllZero Action 0-0-0/ Keep previous reward?

    Starting State:
        ...

    Episode Termination:
        After train through all traffic data
    """

    def __init__(self, config):
        self.test = config["test"]
        self.trafficindex = 0
        self.namespace_resource = 60 #Worker_node_has_60CPUs
        self.service0_SLO = 1200 #house_price_inference_app
        self.service1_SLO = 3000 #sentiment_analysis_app
        self.service2_SLO = 900 #number_recognition_app
        self.service0_action = np.array([[1.5, 10, 1100], [2, 10, 690], [2, 15, 1000], [2.5, 10, 500], [2.5, 15, 730], [2.5, 20, 890], [2.5, 25, 1100], [3, 10, 390], [3, 20, 700], [3, 30, 900], [3, 35, 960], [3.5, 10, 340], [3.5, 20, 530], [3.5, 30, 530], [3.5, 40, 990], [3.5, 45, 1000], [4, 10, 230], [4, 20, 450], [4, 30, 670], [4, 40, 820], [4, 50, 1000], [4, 60, 1100]]) #22 actions
        self.service1_action = np.array([[3, 10, 2500], [4, 10, 1800], [4, 15, 2600], [5, 10, 1400], [5, 15, 2100], [5, 20, 2600], [6, 10, 1100], [6, 15, 1700], [6, 20, 2300], [6, 25, 2900]]) #10 actions
        self.service2_action = np.array([[0.5, 10, 900], [1, 10, 420], [1, 15, 630], [1, 20, 800], [2, 10, 370], [2, 15, 560], [2, 20, 700], [2, 25, 860]]) #8 actions
        self.action_space = spaces.MultiDiscrete([22, 10, 8])
        self.observation_space = spaces.Box(low=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), high=np.array([100, 100, 100, 100, 100, 100, 100, 100, 100]), dtype=int)

        self.state = np.array([1, 1, 56, 1, 1, 56, 1, 1, 1], dtype=int)

    def reset(self, *, seed=None, options=None):
        """Resets the episode.

        Returns:
            Initial observation of the new episode and an info dict.
        """
        self.state = np.array([1, 1, 56, 1, 1, 36, 1, 1, 1], dtype=int)
        self.trafficindex = 0
        # Return initial observation.
        return self.state, {}

    def step(self, action):
        self.trafficindex += 1
        """Takes a single step in the episode given `action`.

        Returns:
            New observation, reward, terminated-flag, truncated-flag, info-dict (empty).
        """
        terminated = False

        if self.trafficindex > 199:
            truncated = True

            service0_sub_reward = self.service0_SLO / self.service0_action[action[0]][2]
            service1_sub_reward = self.service1_SLO / self.service1_action[action[1]][2]
            service2_sub_reward = self.service2_SLO / self.service2_action[action[2]][2]

            service0_resource = math.ceil(self.state[2] / self.service0_action[action[0]][1] / 0.7) * self.service0_action[action[0]][0]
            service1_resource = math.ceil(self.state[5] / self.service1_action[action[1]][1] / 0.7) * self.service1_action[action[1]][0]
            service2_resource = math.ceil(self.state[8] / self.service2_action[action[2]][1] / 0.7) * self.service2_action[action[2]][0]
            total_resource = service0_resource + service1_resource + service2_resource

            if self.namespace_resource < total_resource:
                reward = -100
            else:
                reward = 100*(service0_sub_reward + service1_sub_reward + service2_sub_reward + self.namespace_resource/total_resource)
        else:
            truncated = False
            # if action[0] == 0 or action[1] == 0 or action[2] == 0:
            #     service0_special_reward = self.service0_SLO / 10000
            #     service1_special_reward = self.service1_SLO / 10000
            #     service2_special_reward = self.service2_SLO / 10000
            #     # reward = service0_special_reward + service1_special_reward + service2_special_reward
            #     reward = -1
            #     self.state[2] = Train0[self.trafficindex]
            #     self.state[5] = Train1[self.trafficindex]
            #     self.state[8] = Train2[self.trafficindex]
            #     self.state[0] = int(0)
            #     self.state[1] = int(0)
            #     self.state[3] = int(0)
            #     self.state[4] = int(0)
            #     self.state[6] = int(0)
            #     self.state[7] = int(0)

            # else:
            service0_sub_reward = self.service0_SLO / self.service0_action[action[0]][2]
            service1_sub_reward = self.service1_SLO / self.service1_action[action[1]][2]
            service2_sub_reward = self.service2_SLO / self.service2_action[action[2]][2]

            service0_resource = math.ceil(self.state[2] / self.service0_action[action[0]][1] / 0.7) * self.service0_action[action[0]][0]
            service1_resource = math.ceil(self.state[5] / self.service1_action[action[1]][1] / 0.7) * self.service1_action[action[1]][0]
            service2_resource = math.ceil(self.state[8] / self.service2_action[action[2]][1] / 0.7) * self.service2_action[action[2]][0]
            total_resource = service0_resource + service1_resource + service2_resource
            print(total_resource)


            if self.namespace_resource < total_resource:
              #reward = -1000*(service0_sub_reward + service1_sub_reward + service2_sub_reward)
              #reward = -100*(total_resource/self.namespace_resource)
              reward = -100
              self.state[2] = Train0[self.trafficindex]
              self.state[5] = Train1[self.trafficindex]
              self.state[8] = Train2[self.trafficindex]
              self.state[0] = int(0)
              self.state[1] = int(0)
              self.state[3] = int(0)
              self.state[4] = int(0)
              self.state[6] = int(0)
              self.state[7] = int(0)

            else:
              #reward = (service0_sub_reward + service1_sub_reward + service2_sub_reward)*100
              reward = 100*(service0_sub_reward + service1_sub_reward + service2_sub_reward + self.namespace_resource/total_resource)

              nextstate_service0_resource = service0_resource / self.namespace_resource * 100
              nextstate_service1_resource = service1_resource / self.namespace_resource * 100
              nextstate_service2_resource = service2_resource / self.namespace_resource * 100
              self.state[0] = int(nextstate_service0_resource)
              self.state[3] = int(nextstate_service1_resource)
              self.state[6] = int(nextstate_service2_resource)

              nextstate_service0_latency = self.service0_action[action[0]][2] / self.service0_SLO * 100
              nextstate_service1_latency = self.service1_action[action[1]][2] / self.service1_SLO * 100
              nextstate_service2_latency = self.service2_action[action[2]][2] / self.service2_SLO * 100
              self.state[1] = int(nextstate_service0_latency)
              self.state[4] = int(nextstate_service1_latency)
              self.state[7] = int(nextstate_service2_latency)

              self.state[2] = Train0[self.trafficindex]
              self.state[5] = Train1[self.trafficindex]
              self.state[8] = Train2[self.trafficindex]

        return self.state, reward, terminated, truncated, {}