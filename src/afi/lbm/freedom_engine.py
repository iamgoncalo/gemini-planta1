import math
import numpy as np
import pandas as pd
from datetime import datetime, timezone

class FreedomEngine:
    def __init__(self, zone_id="HORSE_CFT_ZONE_01"):
        self.zone_id = zone_id
        self.history_P = []
        self.history_D = []
        self.window_size = 50 
        
    def compute_perception(self, sensor_data: dict) -> float:
        active_channels = sum(1 for v in sensor_data.values() if v is not None)
        spatial_agents = sensor_data.get('active_agents', 0)
        N_states = max(2, (active_channels * 10) + (spatial_agents * 50))
        T_horizon = 4.0 
        return max(1.0, math.log2(N_states) * T_horizon)

    def compute_distortion(self, sensor_data: dict) -> float:
        temp = sensor_data.get('T_indoor_C', 20.0)
        co2 = sensor_data.get('CO2_ppm', 450)
        O_temp = 1.0 if 18.0 <= temp <= 22.0 else 1.0 + abs(temp - 20.0) * 0.1
        O_co2 = 1.0 if co2 <= 800 else 1.0 + ((co2 - 800) / 400)
        O_total = max(1.0, O_temp * O_co2)
        C_spatial = max(1.0, sensor_data.get('D_spatial', 1.0))
        return max(1.0, (O_total ** 0.5) * (C_spatial ** 0.2))

    def causal_attribution(self, P: float, D: float) -> str:
        if len(self.history_P) < self.window_size: return "BASELINE_LEARNING"
        
        delta_P = (P - np.median(self.history_P)) / max(np.std(self.history_P), 0.1)
        delta_D = (D - np.median(self.history_D)) / max(np.std(self.history_D), 0.1)
        
        if abs(delta_D) > 1.2 * abs(delta_P) and delta_D > 1.0:
            return "D_FAILURE (Physical/Environmental)"
        elif abs(delta_P) > 1.2 * abs(delta_D) and delta_P < -1.0:
            return "P_FAILURE (Sensor/Perception)"
        elif abs(delta_D) > 1.0 or abs(delta_P) > 1.0:
            return "COMBINED_FAILURE (Crowd/Complex)"
        return "NOMINAL"

    def process_timestep(self, sensor_data: dict) -> dict:
        P = self.compute_perception(sensor_data)
        D = self.compute_distortion(sensor_data)
        F = P / D
        status = self.causal_attribution(P, D)
        
        self.history_P.append(P)
        self.history_D.append(D)
        if len(self.history_P) > self.window_size:
            self.history_P.pop(0)
            self.history_D.pop(0)
            
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "zone_id": self.zone_id, "P": round(P, 3), "D": round(D, 3), 
            "F": round(F, 3), "status": status
        }

if __name__ == "__main__":
    engine = FreedomEngine()
    for _ in range(50): engine.process_timestep({'T_indoor_C': 20.0, 'CO2_ppm': 500, 'active_agents': 5})
    
    print("\n--- CAUSAL ATTRIBUTION TESTS ---")
    res1 = engine.process_timestep({'T_indoor_C': 26.0, 'CO2_ppm': 1500, 'active_agents': 5, 'D_spatial': 1.0})
    print(f"Test 1 (HVAC Fail) -> F={res1['F']} | Cause: {res1['status']}")
    
    for _ in range(50): engine.process_timestep({'T_indoor_C': 20.0, 'CO2_ppm': 500, 'active_agents': 5})
    
    res2 = engine.process_timestep({'T_indoor_C': 20.0, 'CO2_ppm': 500, 'active_agents': 0, 'D_spatial': 1.0})
    print(f"Test 2 (Sensor Fail) -> F={res2['F']} | Cause: {res2['status']}")
