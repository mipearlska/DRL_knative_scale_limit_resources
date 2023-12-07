import environment
from sb3_contrib import TRPO

env = environment.ParallelServiceSLO({"test": 10})
#best_model_path = "/tmp/gym/t1/best_model.zip"
finaltrain_model_path = "/root/DRL_limit_resource_knative_scale/TRPOtanh128_Nov29.zip"
model = TRPO.load(finaltrain_model_path, env=env)

# # Get the initial observation (should be: [0.0] for the starting position).
state, info = env.reset()
terminated = truncated = False
total_reward = 0.0
print(model.policy)

# # Play one episode.
#while not terminated and not truncated:
for m in range (19):
    # Compute a single action, given the current observation
    # from the environment.
    print("Input state", state)
    action, _ = model.predict(state)

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