# 🌱 PlantaOS: Digital Twin Operacional Industrial (HORSE CFT)

**Version:** 1.0-MVP (Milestone 5 Delivery)
**Client:** HORSE (Renault Group) / Centro de Formação Técnica (CFT), Aveiro
**Framework:** Architecture of Freedom Intelligence (AFI v6.0)

## Overview
This repository contains the Minimum Viable Product (MVP) for the PlantaOS deployment at the HORSE CFT facility. It transforms static building sensor data into a living, navigating entity governed by the Law of Freedom ($F = P/D$).

## Architecture Stack
The system is built on the AFI Large Behavior Model (LBM) pipeline:
1. **Edge Fusion (`src/afi/edge`)**: Ingests multi-modal spatial data (via OpenClaw).
2. **Freedom Engine (`src/afi/lbm`)**: Calculates $P$ (Perception) and $D$ (Distortion). Performs causal attribution (ΔP vs ΔD).
3. **Digital Twin Visuals (`src/afi/dt/dt03_heatmap.py`)**: Generates spatial F-Field heatmaps.
4. **Financial Engine (`src/afi/dt/dt08_financial_engine.py`)**: Projects ROI, Payback, and NPV.
5. **Conversational Brain (`src/afi/dt/dt10_chatbot.py`)**: Natural Language interface.
6. **Deucalion Optimizer (`src/afi/swarm`)**: Swarm intelligence scripts ready for Deucalion A100 GPU execution.

## Execution
To generate the official MVP delivery report run: `python src/afi/dt/dt_report_generator.py`

## Compliance
This architecture adheres strictly to GDPR and the non-intrusive metadata mandates outlined in the MVP agreement.