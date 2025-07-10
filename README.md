# Enhancing Privacy through Unlinkable Data Sharing with User-in-the-Loop Access Control

This repository contains the code and simulation setup for experiments presented in our study on Enhancing Privacy through Unlinkable Data Sharing with User-in-the-Loop Access Control.

## Repository Structure

- `implementation/`
  - `simulation.py`: Main simulation script.
  - `generate_seed.py`: Script to generate the Zipf distribution.
  - `zipf_50k_seed.json`: Pre-generated Zipf distribution file (50,000 users).
  - `requirements.txt`: Python dependencies.

You can download our simulation results as a compressed archive (~5 GB; ~1.2 million files) here: https://drive.proton.me/urls/GAW8HEDT34#ZHvI5ZpDbBu7

## Reproducing Results

### 1. Prepare the environment

Install Python dependencies:

```bash
pip install -r ./implementation/requirements.txt
```

Install GNU Parallel (if not already installed):

```bash
sudo apt-get install parallel
```

### 2. Generate Zipf distribution (optional)
You can use the provided Zipf distribution (`./implementation/zipf_50k_seed.json`), or generate your own with:

```bash
python3 ./implementation/generate_seed.py
```

### 3. Run simulations
We recommend using GNU Parallel to distribute the workload across multiple CPU cores:

```bash
parallel --jobs 80 \
    'python3 ./implementation/simulation.py --seed "./implementation/zipf_50k_seed.json" --q {1} --r {2} --tau {3} --run {4}' \
    ::: $(seq 0.1 0.1 0.9) ::: $(seq 0.1 0.1 0.9) ::: {1..49} ::: {1..100}
```

Simulation output will be saved under the `./results/` directory.