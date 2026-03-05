#!/bin/bash
#SBATCH --job-name=AFI_LBM_HORSE_CFT
#SBATCH --output=/scratch/goncalo_melo/afi/logs/%j.out
#SBATCH --error=/scratch/goncalo_melo/afi/logs/%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=20:00:00
#SBATCH --account=2025.00020.AIVLAB.DEUCALION

# AFI Phase 2: Large Behavior Model (LBM) Training
# High-quality 20-hour execution limit as requested.

module load python/3.11 cuda/12.2 pytorch/2.2
source /home/goncalo_melo/.venvs/afi/bin/activate

echo "Starting HORSE CFT LBM Optimization on Deucalion (A100)..."
# In production, this points to our full training loop
python /scratch/goncalo_melo/afi/src/afi/lbm/freedom_engine.py
echo "Run complete."
