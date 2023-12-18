import environment
from sb3_contrib import TRPO
import numpy as np

env = environment.Parallel2({"test": 10})
#best_model_path = "/tmp/gym/t1/best_model.zip"
finaltrain_model_path = "/root/DRL_limit_resource_knative_scale/B_tt_TRPOtanh128.zip"
model = TRPO.load(finaltrain_model_path, env=env)

# # Get the initial observation (should be: [0.0] for the starting position).
state, info = env.reset()
terminated = truncated = False
total_reward = 0.0
print(model.policy)

#queuedd = np.array([[21, 1, 3], [21, 1, 3], [21, 1, 0], [21, 3, 0], [21, 1, 3], [21, 1, 3], [21, 1, 2], [21, 1, 0], [21, 1, 0], [21, 1, 0], [21, 1, 0], [21, 1, 7], [21, 1, 2], [6, 1, 0], [14, 1, 3], [15, 1, 0], [21, 1, 3], [20, 1, 7], [20, 1, 3]])
# # Play one episode.
#while not terminated and not truncated:
for m in range (19):
    # Compute a single action, given the current observation
    # from the environment.
    print("Input state", state)
    action, _ = model.predict(state)
    #action = queuedd[m]

    # Apply the computed action in the environment.
    state, reward, terminated, truncated, info = env.step(action)
    print("Action: ", action, "---Reward: ", reward)
    print("Output state", state)
    print("*********")
    print("   ")
    # Sum up rewards for reporting purposes.
    total_reward += reward
# # Report results.

print(f"Played 1 episode; total-reward={total_reward}")