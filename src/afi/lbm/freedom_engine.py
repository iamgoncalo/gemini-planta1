import math
import numpy as np
import pandas as pd
from datetime import datetime

class FreedomEngine:
    """
    AFI Layer 4: Freedom Field Engine (LBM v0).
    Calculates F = P/D across the HORSE CFT environment.
    Performs Causal Decomposition (ΔP vs ΔD) for root-cause anomaly detection.
    """
    
    def __init__(self, zone_id="HORSE_CFT_ZONE_01"):
        self.zone_id = zone_id
        # Rolling baselines for anomaly attribution
        self.history_P = []
        self.history_D = []
        self.window_size = 50 # 50 timesteps for baseline
        
    def compute_perception(self, sensor_data: dict) -> float:
        """
        P = log2(N) * T
        N: Number of distinguishable states (active sensors + spatial resolution)
        T: Predictive depth (horizon)
        """
        # Base sensors (Temp, CO2, Humidity, Power) + OpenClaw spatial agents
        active_channels = sum(1 for v in sensor_data.values() if v is not None)
        spatial_agents = sensor_data.get('active_agents', 0)
        
        N_states = max(2, (active_channels * 10) + (spatial_agents * 50))
        T_horizon = 4.0 # 4-hour LBM lookahead
        
        P = math.log2(N_states) * T_horizon
        return max(1.0, P) # Floor at 1.0 (Passive Regime)

    def compute_distortion(self, sensor_data: dict) -> float:
        """
        Multiplicative D = R^α * O^β * T_b^γ * C^δ * M^ε
        Calibrated for HORSE CFT Industrial environment.
        """
        # Obligation (O): Threshold violations (e.g., Temp outside 18-22C winter band)
        temp = sensor_data.get('T_indoor_C', 20.0)
        co2 = sensor_data.get('CO2_ppm', 450)
        
        O_temp = 1.0 if 18.0 <= temp <= 22.0 else 1.0 + abs(temp - 20.0) * 0.1
        O_co2 = 1.0 if co2 <= 800 else 1.0 + ((co2 - 800) / 400)
        O_total = max(1.0, O_temp * O_co2)
        
        # Spatial Crowding (C): from OpenClaw
        C_spatial = max(1.0, sensor_data.get('D_spatial', 1.0))
        
        # Multiplicative composition (β=0.5 for O, δ=0.2 for C based on AFI calibration)
        D = (O_total ** 0.5) * (C_spatial ** 0.2)
        return max(1.0, D)

    def causal_attribution(self, P: float, D: float) -> str:
        """
        Decomposes anomaly root cause into Perception failure (sensor degradation)
        or Distortion failure (physical environmental spike).
        """
        if len(self.history_P) < self.window_size:
            return "BASELINE_LEARNING"
            
        P_baseline = np.median(self.history_P)
        D_baseline = np.median(self.history_D)
        P_std = max(np.std(self.history_P), 0.1)
        D_std = max(np.std(self.history_D), 0.1)
        
        delta_P = (P - P_baseline) / P_std
        delta_D = (D - D_baseline) / D_std
        
        # If D spikes heavily relative to P drop -> Physical failure (e.g., HVAC broke)
        if abs(delta_D) > 1.2 * abs(delta_P) and delta_D > 1.0:
            return "D_FAILURE (Physical/Environmental)"
        # If P drops heavily relative to D -> Perception failure (e.g., sensor offline)
        elif abs(delta_P) > 1.2 * abs(delta_D) and delta_P < -1.0:
            return "P_FAILURE (Sensor/Perception)"
        elif abs(delta_D) > 1.0 or abs(delta_P) > 1.0:
            return "COMBINED_FAILURE"
            
        return "NOMINAL"

    def process_timestep(self, sensor_data: dict) -> dict:
        P = self.compute_perception(sensor_data)
        D = self.compute_distortion(sensor_data)
        F = P / D
        
        # Causal Attribution
        status = self.causal_attribution(P, D)
        
        # Update rolling baselines
        self.history_P.append(P)
        self.history_D.append(D)
        if len(self.history_P) > self.window_size:
            self.history_P.pop(0)
            self.history_D.pop(0)
            
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "zone_id": self.zone_id,
            "P_value": round(P, 3),
            "D_value": round(D, 3),
            "F_value": round(F, 3),
            "status": status
        }

if __name__ == "__main__":
    engine = FreedomEngine()
    print("--- AFI Freedom Engine Initialized ---")
    
    # Simulate a sudden CO2 spike (Distortion failure)
    print("\nSimulating 50 nominal timesteps...")
    for _ in range(50):
        engine.process_timestep({'T_indoor_C': 20.5, 'CO2_ppm': 500, 'active_agents': 5})
        
    print("Injecting Anomaly: CO2 spikes to 1400ppm (Training Room crowded)")
    anomaly_data = {'T_indoor_C': 21.0, 'CO2_ppm': 1400, 'active_agents': 35, 'D_spatial': 2.5}
    result = engine.process_timestep(anomaly_data)
    
    print(f"Result: F={result['F_value']} | Root Cause: {result['status']}")
