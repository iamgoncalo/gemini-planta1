import numpy as np
import pandas as pd

class PlantaFinancialEngine:
    """
    AFI Digital Twin Layer 08: Financial & ROI Engine
    Translates F-Field optimization (ΔF) into EUR savings for the HORSE CFT.
    Uses real 2025 consumption data.
    """
    
    def __init__(self):
        # 1. Real 2025 Energy Data (HORSE CFT) - 7 active months (July excluded)
        self.energy_2025_kWh = {
            "MAY": 3659.0, "JUN": 2760.0, "AUG": 2290.5, 
            "SEP": 3291.0, "OCT": 3400.0, "NOV": 2205.0, "DEC": 2062.5
        }
        self.active_months = len(self.energy_2025_kWh)
        self.total_recorded_kWh = sum(self.energy_2025_kWh.values())
        
        # Annualized estimate (Extrapolating the 7 months to 12)
        self.annual_baseline_kWh = self.total_recorded_kWh * (12 / self.active_months)
        
        # 2. Financial Parameters
        self.eur_per_kWh = 0.14
        self.annual_maintenance_baseline_eur = 12000.0 # Estimated facility baseline
        
        # 3. PlantaOS Costs
        self.capex_install_eur = 15000.0 # MVP Hardware/Software Setup
        self.opex_subscription_eur = 500.0 # Annual Intelligence Subscription

    def calculate_roi(self, optimized_F_global: float, baseline_F_global: float = 0.65):
        """
        Calculates financial impact based on the Freedom (F) improvement.
        According to AFI, reducing Distortion (D) by increasing F yields:
        - Max 25% energy reduction
        - Max 30% maintenance reduction
        """
        print("="*60)
        print(" PLANTA OS - FINANCIAL PROJECTION (HORSE CFT) ")
        print("="*60)
        
        # Calculate Improvement Delta
        f_improvement_pct = max(0, (optimized_F_global - baseline_F_global) / baseline_F_global)
        
        # 1. Energy Savings (Scale to max 25% based on F improvement)
        energy_saving_factor = min(0.25, f_improvement_pct * 0.5) 
        saved_kWh = self.annual_baseline_kWh * energy_saving_factor
        saved_energy_eur = saved_kWh * self.eur_per_kWh
        
        # 2. Maintenance Savings (Scale to max 30% based on F improvement)
        maintenance_saving_factor = min(0.30, f_improvement_pct * 0.6)
        saved_maintenance_eur = self.annual_maintenance_baseline_eur * maintenance_saving_factor
        
        total_annual_savings = saved_energy_eur + saved_maintenance_eur
        net_annual_cashflow = total_annual_savings - self.opex_subscription_eur
        
        payback_years = self.capex_install_eur / net_annual_cashflow if net_annual_cashflow > 0 else float('inf')
        
        # 10-Year NPV (Assuming 5% discount rate)
        discount_rate = 0.05
        years = np.arange(1, 11)
        cash_flows = np.full(10, net_annual_cashflow)
        npv = np.sum(cash_flows / ((1 + discount_rate) ** years)) - self.capex_install_eur
        
        print(f"Building Baseline:     {self.annual_baseline_kWh:,.0f} kWh/year")
        print(f"F-Field Optimization:  {baseline_F_global:.2f} -> {optimized_F_global:.2f} (+{f_improvement_pct*100:.1f}%)")
        print("-" * 60)
        print(f"Energy Savings:        €{saved_energy_eur:,.2f} / year (-{energy_saving_factor*100:.1f}%)")
        print(f"Maintenance Savings:   €{saved_maintenance_eur:,.2f} / year (-{maintenance_saving_factor*100:.1f}%)")
        print(f"Gross Annual Savings:  €{total_annual_savings:,.2f}")
        print(f"Net Annual Cashflow:   €{net_annual_cashflow:,.2f} (post-subscription)")
        print("-" * 60)
        print(f"CAPEX (Install):       €{self.capex_install_eur:,.2f}")
        print(f"Payback Period:        {payback_years:.1f} years")
        print(f"10-Year NPV:           €{npv:,.2f}")
        print("="*60)
        
        return {
            "net_annual_cashflow": net_annual_cashflow,
            "payback_years": payback_years,
            "npv_10_yr": npv
        }

if __name__ == "__main__":
    engine = PlantaFinancialEngine()
    # We pass the optimal F_global = 0.95 (achieved in our Swarm step)
    engine.calculate_roi(optimized_F_global=0.95, baseline_F_global=0.65)
