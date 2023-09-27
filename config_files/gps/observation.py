from sumo_rl.environment.observations import ObservationFunction
from sumo_rl.environment.traffic_signal import TrafficSignal
import numpy as np
from gymnasium import spaces

class ModelGpsObservationFunction(ObservationFunction):
    def __init__(self, ts: TrafficSignal):
        super().__init__(ts)

    def __call__(self) -> np.ndarray:
        """Return the custom observation."""
        # density = self.ts.get_lanes_density_hidden()
        queue = self.ts.get_lanes_queue_hidden()
        occupancy = self.ts.get_occupancy_per_lane_hidden() #occupancy within 35m
        # wait_times = self.ts.get_accumulated_waiting_time_per_lane_hidden()
        avg_speeds = self.ts.get_average_lane_speeds_hidden()
        phase_times = self.ts.get_times_since_phase_selected()
        # print()
        # print(f"Density = {density}")
        # print(f"Queue = {queue}")
        # print(f"Occupancy = {occupancy}")
        # print(f"Wait times = {wait_times}")
        # print(f"Avg speeds = {avg_speeds}")
        # print(f"Phase times = {phase_times}")
        # print()
        observation = np.array(queue + occupancy + avg_speeds + phase_times, dtype=np.float32)
        return observation

    def observation_space(self) -> spaces.Box:
        """Return the observation space."""
        return spaces.Box(
            low=np.zeros(3*len(self.ts.lanes) + self.ts.num_green_phases, dtype=np.float32),
            high=np.ones(3*len(self.ts.lanes) + self.ts.num_green_phases, dtype=np.float32),
        )
    
class GreedyGpsObservationFunction(ObservationFunction):
    def __init__(self, ts: TrafficSignal):
        super().__init__(ts)

    def __call__(self) -> np.ndarray:
        """Return the custom observation."""
        density = self.ts.get_lanes_density_hidden()
        observation = np.array(density, dtype=np.float32)
        return observation

    def observation_space(self) -> spaces.Box:
        """Return the observation space."""
        return spaces.Box(
            low=np.zeros(len(self.ts.lanes), dtype=np.float32),
            high=np.ones(len(self.ts.lanes), dtype=np.float32),
        )
    
class MaxPressureGpsObservationFunction(ObservationFunction):
    def __init__(self, ts: TrafficSignal):
        super().__init__(ts)

    def __call__(self) -> np.ndarray:
        """Return the custom observation."""
        pressure = self.ts.get_lanes_pressure_hidden()
        observation = np.array(pressure, dtype=np.float32)
        return observation

    def observation_space(self) -> spaces.Box:
        """Return the observation space."""
        return spaces.Box(
            low=np.zeros(len(self.ts.lanes), dtype=np.float32),
            high=np.ones(len(self.ts.lanes), dtype=np.float32),
        )