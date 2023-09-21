from stable_baselines3 import PPO
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import VecMonitor
import supersuit as ss
import sumo_rl
from supersuit.multiagent_wrappers import pad_observations_v0
from supersuit.multiagent_wrappers import pad_action_space_v0

from config_files.observation_class_directories import get_observation_class
from config_files.custom_reward import my_reward_fn
from config_files.net_route_directories import get_file_locations
from config_files.delete_results import deleteSimulationResults

# PARAMETERS
#======================
# In each timestep (delta_time), the agent takes an action, and the environment (the traffic simulation) advances by delta_time seconds. 
# The agent continues to take actions for totalTimesteps. 

numSeconds = 3600 # This parameter determines the total duration of the SUMO traffic simulation in seconds.
deltaTime = 5 #This parameter determines how much time in the simulation passes with each step.
simRepeats = 8 # Number of episodes
parallelEnv = 1
totalTimesteps = numSeconds*simRepeats*parallelEnv # This is the total number of steps in the environment that the agent will take for training. It’s the overall budget of steps that the agent can interact with the environment.
map = 'cologne8'
mdl = 'PPO' # Set to DQN for DQN model
observation = 'custom' #camera, gps, custom
seed = '12345' # or 'random'
gui = True # Set to True to see the SUMO-GUI
hide_cars = False # Required true for GPS observation, won't affect other observation functions, just changes colours of cars
add_system_info = True
net_route_files = get_file_locations(map) # Select a map

# Remove results
deleteSimulationResults(map, mdl, observation)

# Get observation class
observation_class = get_observation_class("model", observation)

sim_path = f"./results/sim/{map}-{mdl}-{observation}"

# creates a SUMO environment with multiple intersections, each controlled by a separate agent.
env = sumo_rl.parallel_env(
    net_file=net_route_files["net"],
    route_file=net_route_files["route"],
    use_gui=gui,
    num_seconds=numSeconds, 
    delta_time=deltaTime, 
    out_csv_name=sim_path,
    sumo_seed = seed,
    reward_fn=my_reward_fn,
    observation_class=observation_class,
    hide_cars = hide_cars
)

env = pad_action_space_v0(env) # pad_action_space_v0 function pads the action space of each agent to be the same size. This is necessary for the environment to be compatible with stable-baselines3.
env = pad_observations_v0(env) # pad_observations_v0 function pads the observation space of each agent to be the same size. This is necessary for the environment to be compatible with stable-baselines3.
env = ss.pettingzoo_env_to_vec_env_v1(env) # pettingzoo_env_to_vec_env_v1 function vectorizes the PettingZoo environment, allowing it to be used with standard single-agent RL methods.
env = ss.concat_vec_envs_v1(env, 1, num_cpus=1, base_class="stable_baselines3") # function creates 4 copies of the environment and runs them in parallel. This effectively increases the number of agents by 4 times, as each copy of the environment has its own set of agents.
env = VecMonitor(env)

if mdl == 'PPO':
      model = PPO(
          env=env,
          policy="MlpPolicy",
      )
elif mdl == 'DQN':
      model = DQN(
          env=env,
          policy="MlpPolicy",
      )

# Run a manual simulation
model.set_parameters(f"./models/best_model_{map}_{mdl}_{observation}", exact_match=True, device='auto')
avg_rewards = []
obs = env.reset()
done = False
while not done:
    actions = model.predict(obs, deterministic=True)[0]
    obs, rewards, dones, infos = env.step(actions)
    avg_rewards.append(sum(rewards)/len(rewards))
    done = dones.any()

print(f"\nMean reward for manual simulation= {sum(avg_rewards)/len(avg_rewards)}\n")
env.close()