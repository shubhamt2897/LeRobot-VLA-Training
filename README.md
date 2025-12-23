# LeRobot-VLA-Training

<p align="center">
  <img src="https://raw.githubusercontent.com/huggingface/lerobot/main/media/lerobot-logo-thumbnail.png" width="200">
</p>

## 🎯 Project Overview

This project was developed during the **Robot Hackathon** organised by **RoboTUM** with the goal of training a Vision-Language-Action (VLA) model to make the **LeRobot SO-101 robot arm write numbers**. The project explores two distinct solutions:

### Solution 1: GROOT N1.5 VLA Training
Vision-Language-Action approach using **GROOT N1.5** - a language-conditioned policy that can understand text instructions like "write digit 5". Unlike ACT (Action Chunking Transformer), GROOT supports language input, which is essential for our use case where we need to specify which digit to write.

### Solution 2: GPT Agent for Multi-Digit Writing
An agentic approach using **GPT** to decode and generate parquet files for multi-digit number writing, enabling the robot to write arbitrary number sequences by understanding digit translations.

### Why GROOT over ACT?
- **ACT** is vision-to-action only - it cannot accept language/text instructions
- **GROOT** is a true VLA model that conditions actions on both vision AND language
- For digit writing, we need to tell the robot "write 3" or "write 7" - this requires language understanding

### 🖥️ Development Environment
Training was performed on **NVIDIA's Brev platform** GPU Instance.


## 📸 Our Setup

<p align="center">
  <img src="images and video/WhatsApp Image 2025-12-07 at 17.10.11.jpeg" width="45%" alt="Teleoperation Follower Setup">
  <img src="images and video/WhatsApp Image 2025-12-08 at 13.44.07.jpeg" width="45%" alt="Teleoperation Leader Setup">
   <img src="images and video\WhatsApp Image 2025-12-08 at 13.44.07 (2).jpeg" width="45%" alt="Teleoperation Setup">
</p>

*Our teleoperation setup with SO-101 leader and follower arms*

---

## 📁 Project Structure

```
LeRobot-VLA-Training/
├── README.md                    # This file
├── requirements.txt            # Dependencies (lerobot installed via pip)
├── Hackathon.txt               # Hardware setup notes and CLI commands
├── robotum_lerobot_ppt.pdf     # Presentation slides
├── images and video/           # Demo recordings
└── datasets/                   # Custom teleoperated datasets
    ├── S101_pm_0/              # Dataset for digit "0"
    ├── S101_pm_1/              # Dataset for digit "1"
    ├── ...                     # Datasets for digits 2-8
    └── S101_pm_9/              # Dataset for digit "9"
```

> **Note:** LeRobot framework is installed via pip (see requirements.txt), not included in this repo.

---

## 🛠️ Hardware Setup

### Robot Components
- **LeRobot SO-101 Follower Arm** (6-DOF robot arm)
- **SO-101 Leader Arm** (Teleoperation controller)
- **Intel RealSense Camera** (Bird's eye view, 848x480 @ 30fps) - **Primary camera used**

> **Note:** We initially experimented with a wrist-mounted USB webcam, but the recordings from it were not suitable for training. We ended up using only the Intel RealSense camera for the bird's eye view, which provided much better quality data for our number-writing task.

### Port Configuration
| Component | Port |
|-----------|------|
| Leader Arm | COM4 |
| Follower Arm | COM3 |

---

## 🚀 Getting Started

### Prerequisites

```bash
# Clone this repository
git clone https://github.com/shubhamt2897/LeRobot-VLA-Training.git
cd LeRobot-VLA-Training

# Install dependencies (includes LeRobot)
pip install -r requirements.txt

# Or install LeRobot directly from source for latest features
pip install git+https://github.com/huggingface/lerobot.git

# For Windows, additional requirements
pip install pyrealsense2  # Intel RealSense support
```

### 🖥️ Setup CLI Tool (Work in Progress)

I am  develoworking on an interactive CLI tool to simplify robot setup and calibration:

```powershell
# Install CLI dependencies
pip install textual rich

# Run the interactive setup
python tools/setup_cli.py
```

**Features:**
- 🎮 Interactive TUI with keyboard and mouse support
- ⚙️ Port configuration wizard
- 📷 Camera setup helper
- ✅ Step-by-step calibration guide

> ⚠️ **Note:** This tool is a work in progress. Arrow key navigation and some features may not work perfectly on all terminals. For best results, use **Anaconda Prompt**, **Windows Terminal**, or **PowerShell 7+**.

### 1. Find Robot Ports

```powershell
lerobot-find-port
```

### 2. Setup Motors

```powershell
#Use your port name in the  setups
# Leader arm
lerobot-setup-motors --teleop.type=so101_leader --teleop.port=COM4

# Follower arm
lerobot-setup-motors --teleop.type=so101_leader --teleop.port=COM3
```

### 3. Calibrate Robot Arms

```powershell
# Calibrate leader arm
lerobot-calibrate --teleop.type=so101_leader --teleop.port=COM4 --teleop.id=Leader

# Calibrate follower arm
lerobot-calibrate --robot.type=so101_follower --robot.port=COM3 --robot.id=Follower
```

### 4. Test Teleoperation

```powershell
# Basic teleoperation (no cameras)
lerobot-teleoperate --teleop.type=so100_leader --teleop.port=COM4 --teleop.id=Leader --robot.type=so101_follower --robot.port=COM3 --robot.id=Follower

# With Intel RealSense camera (bird's eye view) - This is what we used
lerobot-teleoperate --robot.type=so101_follower --robot.port="COM3" --robot.id=Follower --robot.cameras="{ front: {type: intelrealsense, serial_number_or_name: 218622273423, width: 848, height: 480, fps: 30, use_depth: true} }" --teleop.type=so101_leader --teleop.port="COM4" --teleop.id=Leader --display_data=True
```

---

## 📊 Dataset Collection

### Record Demonstrations

```powershell
# Record dataset for digit "0" (using Intel RealSense bird's eye view)
lerobot-record --robot.type=so101_follower --robot.port=COM3 --robot.id=Follower --robot.cameras="{ front: {type: intelrealsense, serial_number_or_name: 218622273423, width: 848, height: 480, fps: 30, use_depth: true} }" --teleop.type=so101_leader --teleop.port=COM4 --teleop.id=Leader --dataset.repo_id=your_Dataset_dir --dataset.local_files_only=true
```

### Dataset Structure

Each dataset contains:
```
S101_X/
├── data/
│   └── chunk-000/
│       └── file-000.parquet    # Action/observation data
├── meta/
│   ├── info.json              # Dataset metadata
│   ├── stats.json             # Normalization statistics
│   ├── tasks.parquet          # Task descriptions
│   └── episodes/              # Episode information
└── videos/
    └── observation.images.front/  # Intel RealSense bird's eye view
```

### Using Datasets from HuggingFace Hub

LeRobot supports loading datasets directly from the HuggingFace Hub. Use the `--dataset.repo_id` flag in training commands to specify the dataset.

---

## 🧠 Training Policies

### VLA Models Comparison

This hackathon focused on **Vision-Language-Action (VLA)** model implementation. VLA models are essential for tasks requiring language instructions - like telling the robot "write digit 5". Here's a comparison of available VLA models:

| VLA Model | Architecture | Language Encoder | Vision Encoder | Parameters | Best For |
|-----------|-------------|------------------|----------------|------------|----------|
| **GROOT N1.5** | Transformer | LLM-based | Vision Transformer | Large | High-quality manipulation with rich language understanding |
| **SmolVLA** | Lightweight Transformer | Smaller LM | Efficient ViT | ~1B | Edge deployment, faster inference |
| **OpenVLA** | LLaMA + ViT | LLaMA | SigLIP | 7B | General-purpose robotics |
| **RT-2** | PaLM-E based | PaLM | ViT | 55B | Complex reasoning tasks |
| **Octo** | Transformer | T5 | ResNet | 93M | Lightweight, fast fine-tuning |



### Dataset Folder Naming

Each folder in `shubhamt0802/` corresponds to a single digit:
- `S101_pm_0/` - Dataset for writing digit "0"
- `S101_pm_1/` - Dataset for writing digit "1"
- `S101_pm_2/` - Dataset for writing digit "2"
- ... and so on up to `S101_pm_9/`

---

### 🔗 Combining Datasets

Before training, merge all digit datasets into a single combined dataset. This allows one model to learn all digits 0-9.

```bash
# Merge all digit datasets (0-9) into one combined dataset
python -m lerobot.scripts.lerobot_edit_dataset \
    --repo_id datasets/S101_all_digits \
    --root ./datasets \
    --operation.type merge \
    --operation.repo_ids "['datasets/S101_pm_0', 'datasets/S101_pm_1', 'datasets/S101_pm_2', 'datasets/S101_pm_3', 'datasets/S101_pm_4', 'datasets/S101_pm_5', 'datasets/S101_pm_6', 'datasets/S101_pm_7', 'datasets/S101_pm_8', 'datasets/S101_pm_9']"
```

This creates a new dataset `S101_all_digits/` containing all episodes from digits 0-9.

---

### Training on Combined Dataset

After merging, train GROOT on the combined dataset with language conditioning:

```bash
# Train GROOT N1.5 on ALL digits (combined dataset)
# GROOT uses language prompts like "write digit 5" to condition the policy
# We used 50000 steps - increase for better results
python -m lerobot.scripts.train \
  --dataset.repo_id=datasets/S101_all_digits \
  --dataset.root=./datasets \
  --policy.type=groot_n1 \
  --output_dir=outputs/train/groot_all_digits \
  --training.num_steps=50000 \
  --device=cuda
```

### Alternative: SmolVLA (Lightweight VLA)

```bash
# SmolVLA - smaller VLA model, also supports language input
python -m lerobot.scripts.train \
  --dataset.repo_id=datasets/S101_all_digits \
  --dataset.root=./datasets \
  --policy.type=smolvla \
  --output_dir=outputs/train/smolvla_all_digits \
  --training.num_steps=50000 \
  --device=cuda
```

### Note on Non-VLA Policies

Policies like ACT, Diffusion, and VQBET do NOT support language input. They would require training separate models for each digit, which is inefficient:

```bash
# Example: ACT would need separate training per digit (NOT recommended)
# python -m lerobot.scripts.train --policy.type=act --dataset.repo_id=datasets/S101_pm_0  # Only digit 0
# python -m lerobot.scripts.train --policy.type=act --dataset.repo_id=datasets/S101_pm_1  # Only digit 1
# ... and so on - inefficient!
```

---

## 🤖 Solution 2: GPT Agent for Multi-Digit Writing

### Concept

Instead of training separate models for each number combination, we use a GPT agent to:
1. Parse the target multi-digit number
2. Decode individual digit trajectories
3. Generate combined parquet files with proper translations between digits
4. Handle positioning and spacing automatically

### Implementation

The GPT agent analyzes the saved single-digit datasets and creates combined trajectories by:
1. Loading individual digit trajectories from the dataset
2. Calculating appropriate translation offsets for spacing
3. Combining movements into a single parquet file

### Combined Datasets

The `lerobot/data/` folder contains pre-generated combined number datasets:
- `combined_number_21/` - Trajectory for writing "21"
- `combined_number_45/` - Trajectory for writing "45"
- `combined_number_68/` - Trajectory for writing "68"
- etc.

---

## 📈 Evaluation

### Replay Recorded Episodes

```powershell
lerobot-replay --robot.type=so101_follower --robot.port=COM3 --robot.id=Follower --dataset.repo_id=shubhamt0802/S101_0 --dataset.local_files_only=true --episode=0
```

### Evaluate Trained GROOT Policy

```powershell
# Evaluate GROOT with language prompt
lerobot-eval --policy.path=outputs/groot_all_digits/checkpoint --robot.type=so101_follower --robot.port=COM3 --robot.id=Follower --robot.cameras="{ front: {type: intelrealsense, serial_number_or_name: 218622273423, width: 848, height: 480, fps: 30, use_depth: true} }"
```

---

## 🔧 Troubleshooting

### Common Issues

1. **Camera not found**: Check camera index with `lerobot-find-cameras`

2. **Motor communication error**: Verify COM ports and run `lerobot-setup-motors`

3. **CUDA out of memory**: Reduce `batch_size` or `chunk_size`

4. **Dataset loading error**: Ensure you're using the correct `--dataset.root` path

5. **Teleoperation stops unexpectedly**: 
   - This can happen during recording sessions
   - **Solution**: Delete the recorded episodes from cache and redo the complete recording set
   - Cache location is typically in your dataset folder or `.cache` directory

6. **Follower arm gets stuck/unresponsive**:
   - The robot follower arm may become unresponsive during operation
   - **Solution**: Disconnect power from the follower arm, wait a few seconds, and reconnect it

---

## 🎓 What We Learned

During this hackathon project, we gained hands-on experience with:

### Vision-Language-Action (VLA) Models
- Understanding how VLA models bridge vision, language, and robotic actions
- Why language conditioning is essential for tasks requiring instruction-following
- GROOT N1.5 as a powerful VLA that accepts text prompts to guide robot behavior
- Key difference: ACT/Diffusion are vision-only, while GROOT/SmolVLA accept language

### Imitation Learning
- Collecting human demonstrations through teleoperation
- Training policies to mimic expert behavior from demonstration data
- Understanding the importance of data quality and quantity for policy performance

### Policy Architecture Trade-offs
- **ACT**: Fast, precise, but no language input - need separate model per task
- **GROOT**: Language-conditioned, single model can handle multiple tasks via prompts
- Choosing the right architecture based on task requirements

### Teleoperation
- Setting up leader-follower robot arm systems
- Recording synchronized video and action data
- Challenges of real-world data collection (camera positioning, motion quality)

### Robot Hardware
- Motor configuration and calibration for SO-101 arms
- Camera setup (Intel RealSense) for visual observations
- Debugging hardware communication issues

---

## 📚 References

- [LeRobot Documentation](https://huggingface.co/docs/lerobot/index)
- [SO-101 Tutorial](https://huggingface.co/docs/lerobot/so101)
- [GROOT N1 - NVIDIA](https://developer.nvidia.com/isaac/groot)
- [Vision-Language-Action Models](https://huggingface.co/blog/vla)
- [HuggingFace LeRobot Hub](https://huggingface.co/lerobot)


## 📄 License

This project uses the [LeRobot framework](https://github.com/huggingface/lerobot) which is licensed under Apache-2.0.
