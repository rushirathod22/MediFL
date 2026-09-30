# ============================================================
#  MediFL — Federated Learning Training on Google Colab
#  Dataset: NIH Chest X-Ray 14 (Kaggle Subset)
#  Sr. No. 29 — Privacy-Preserving Federated AI Framework
# ============================================================
#
#  HOW TO USE:
#  1. Open Google Colab → https://colab.research.google.com
#  2. File → Upload Notebook → Upload this .py file  (OR)
#     File → New Notebook → paste each cell block below
#  3. Runtime → Change Runtime Type → GPU (T4)
#  4. Run cells top to bottom (Shift+Enter)
# ============================================================


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 1 — Install Dependencies                          ║
# ╚══════════════════════════════════════════════════════════╝

"""
!pip install torch torchvision opacus opendatasets Pillow matplotlib scikit-learn gdown -q
print("✅ All packages installed!")
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 2 — Download Dataset (3 Easy Options — Pick ONE)  ║
# ╚══════════════════════════════════════════════════════════╝
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✅ OPTION A (EASIEST) — opendatasets (Just type username + key)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Go to https://www.kaggle.com → Your Profile → Account
# 2. Scroll to API section → Click "Create New API Token"
# 3. Open the downloaded kaggle.json → note username and key values
# 4. Run this cell → it will prompt you to type username and key

"""
import opendatasets as od
import os

# It will ask: "Please provide your Kaggle credentials."
# Enter your Kaggle Username and Key when prompted — no file upload needed!
od.download('https://www.kaggle.com/datasets/nih-chest-xrays/sample',
            data_dir='/content/')

DATA_DIR = '/content/sample'
print("✅ Dataset downloaded via opendatasets!")
!ls /content/sample/
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✅ OPTION B — Use COVID-19 X-Ray Dataset (NO login needed!)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Smaller (1.8 GB), same binary classification task
# Direct download — no Kaggle account required

"""
import gdown, zipfile, os

# Direct Google Drive link for COVID-19 Radiography dataset
url = 'https://drive.google.com/uc?id=1lBCytQEFxCJVFGmhrNmPBnfqFJFjSUiW'
output = '/content/covid_xray.zip'

gdown.download(url, output, quiet=False)
with zipfile.ZipFile(output, 'r') as z:
    z.extractall('/content/covid_data/')

DATA_DIR = '/content/covid_data'
print("✅ COVID-19 X-Ray dataset downloaded — NO login required!")
!ls /content/covid_data/
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✅ OPTION C — Manual Upload from your PC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Download the dataset manually from Kaggle website (no API needed)
#    Link: https://www.kaggle.com/datasets/nih-chest-xrays/sample
# 2. Extract the zip file on your PC
# 3. Zip a small folder of images (~500 images)
# 4. Run this cell to upload it to Colab

"""
from google.colab import files
import zipfile, os

print("📁 Upload your dataset zip file (select from your PC)...")
uploaded = files.upload()

zip_name = list(uploaded.keys())[0]
with zipfile.ZipFile(zip_name, 'r') as z:
    z.extractall('/content/nih_data/')

DATA_DIR = '/content/nih_data'
print("✅ Dataset uploaded and extracted!")
!ls /content/nih_data/
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 3 — Import Libraries                              ║
# ╚══════════════════════════════════════════════════════════╝

"""
import os
import copy
import random
import hashlib
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import transforms, models

# Set seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

# Use GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"✅ Using device: {device}")
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 4 — Load & Explore NIH Dataset                    ║
# ╚══════════════════════════════════════════════════════════╝

"""
DATA_DIR = '/content/nih_data'

# Find the CSV labels file
csv_file = None
for f in os.listdir(DATA_DIR):
    if f.endswith('.csv'):
        csv_file = os.path.join(DATA_DIR, f)
        break

df = pd.read_csv(csv_file)
print(f"✅ Dataset loaded: {len(df)} records")
print(df.head())
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nLabel distribution:")
print(df['Finding Labels'].value_counts().head(10))
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 5 — Preprocess: Binary Labels (Normal vs Disease) ║
# ╚══════════════════════════════════════════════════════════╝

"""
# Binary classification: Normal=0, Disease=1
def get_binary_label(label_str):
    return 0 if label_str.strip() == 'No Finding' else 1

df['binary_label'] = df['Finding Labels'].apply(get_binary_label)

# Find image folder
img_folder = None
for root, dirs, files in os.walk(DATA_DIR):
    for d in dirs:
        sample_path = os.path.join(root, d)
        if any(f.endswith('.png') for f in os.listdir(sample_path)):
            img_folder = sample_path
            break
    if img_folder:
        break

# Filter to only rows where image exists
available_images = set(os.listdir(img_folder))
df = df[df['Image Index'].isin(available_images)].reset_index(drop=True)

print(f"✅ Available images: {len(df)}")
print(f"   Normal (0): {(df['binary_label']==0).sum()}")
print(f"   Disease (1): {(df['binary_label']==1).sum()}")
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 6 — Custom NIH Dataset Class                      ║
# ╚══════════════════════════════════════════════════════════╝

"""
class NIHChestDataset(Dataset):
    \"\"\"NIH Chest X-Ray Dataset loader for MediFL hospital nodes.\"\"\"

    def __init__(self, dataframe, img_folder, transform=None):
        self.df = dataframe.reset_index(drop=True)
        self.img_folder = img_folder
        self.transform = transform or transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=3),  # Convert to 3-ch
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        img_name = self.df.loc[idx, 'Image Index']
        label = self.df.loc[idx, 'binary_label']
        img_path = os.path.join(self.img_folder, img_name)

        image = Image.open(img_path).convert('RGB')
        image = self.transform(image)
        return image, torch.tensor(label, dtype=torch.long)

print("✅ NIHChestDataset class defined!")
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 7 — Split Into 3 Hospital Partitions              ║
# ╚══════════════════════════════════════════════════════════╝

"""
# Shuffle dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
total = len(df)

# Hospital partitions (simulating real-world data distribution)
split_A = int(0.50 * total)   # Hospital A (Mumbai)  → 50%
split_B = int(0.30 * total)   # Hospital B (Pune)    → 30%
# Hospital C (Delhi)           → 20% (remainder)

df_hospital_A = df.iloc[:split_A]
df_hospital_B = df.iloc[split_A:split_A + split_B]
df_hospital_C = df.iloc[split_A + split_B:]

print("✅ Dataset split into 3 hospital partitions:")
print(f"   🏥 Hospital A (Mumbai): {len(df_hospital_A)} samples (50%)")
print(f"   🏥 Hospital B (Pune):   {len(df_hospital_B)} samples (30%)")
print(f"   🏥 Hospital C (Delhi):  {len(df_hospital_C)} samples (20%)")
print(f"   📊 Total: {total} samples — Zero data shared between hospitals!")
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 8 — Diagnostic Model (MobileNetV2 Transfer Learn) ║
# ╚══════════════════════════════════════════════════════════╝

"""
class DiagnosticModel(nn.Module):
    \"\"\"
    MobileNetV2-based diagnostic model for chest X-ray classification.
    Lightweight enough for federated training across hospital nodes.
    \"\"\"
    def __init__(self, num_classes=2):
        super(DiagnosticModel, self).__init__()
        # Use pretrained MobileNetV2 as feature extractor
        backbone = models.mobilenet_v2(pretrained=True)
        # Freeze feature extraction layers
        for param in backbone.features.parameters():
            param.requires_grad = False
        # Replace classifier head
        backbone.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(backbone.last_channel, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )
        self.model = backbone

    def forward(self, x):
        return self.model(x)

# Test model
test_model = DiagnosticModel(num_classes=2).to(device)
test_input = torch.randn(2, 3, 224, 224).to(device)
test_out = test_model(test_input)
print(f"✅ DiagnosticModel defined! Output shape: {test_out.shape}")
del test_model, test_input, test_out
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 9 — Federated Learning Core (FedAvg)              ║
# ╚══════════════════════════════════════════════════════════╝

"""
# --- FedAvg Aggregation ---
def fedavg_aggregate(global_model, local_models, num_samples_list):
    \"\"\"
    Federated Averaging: W_global = Σ (n_k / N_total) * W_k
    Raw patient data NEVER leaves hospital — only weights are shared.
    \"\"\"
    total_samples = sum(num_samples_list)
    global_dict = global_model.state_dict()

    for key in global_dict.keys():
        # Weighted average of each layer
        global_dict[key] = sum(
            (n / total_samples) * local_models[i].state_dict()[key].float()
            for i, n in enumerate(num_samples_list)
        )
    global_model.load_state_dict(global_dict)
    return global_model


# --- Compute SHA-256 hash of model weights (Audit trail) ---
def compute_model_hash(model):
    weights_str = json.dumps(
        {k: v.cpu().numpy().tolist() for k, v in model.state_dict().items()},
        default=str
    )
    return hashlib.sha256(weights_str.encode()).hexdigest()


# --- Local Training at Hospital Node ---
def train_hospital_node(hospital_name, dataframe, img_folder, global_model,
                        epochs=2, lr=0.001, batch_size=32):
    \"\"\"
    Each hospital trains the global model on LOCAL data only.
    Only model weights are returned — NOT the patient images.
    \"\"\"
    print(f"   🏥 [{hospital_name}] Starting local training on {len(dataframe)} samples...")

    dataset = NIHChestDataset(dataframe, img_folder)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True,
                        num_workers=2, pin_memory=True)

    # Load global model weights into local copy
    local_model = DiagnosticModel(num_classes=2).to(device)
    local_model.load_state_dict(copy.deepcopy(global_model.state_dict()))

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, local_model.parameters()), lr=lr
    )

    local_model.train()
    total_loss, correct, total = 0.0, 0, 0

    for epoch in range(epochs):
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = local_model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    avg_loss = total_loss / total
    accuracy = correct / total * 100
    print(f"   ✅ [{hospital_name}] Done — Loss: {avg_loss:.4f} | Acc: {accuracy:.2f}%")

    # Return local model weights and metrics (NO raw data returned)
    return local_model, len(dataframe), avg_loss, accuracy

print("✅ Federated Learning functions defined!")
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 10 — Run Federated Training (5 Rounds)            ║
# ╚══════════════════════════════════════════════════════════╝

"""
# ── Configuration ──────────────────────────────────────────
FL_ROUNDS     = 5     # Number of federated rounds
LOCAL_EPOCHS  = 2     # Local training epochs per hospital per round
LEARNING_RATE = 0.001
BATCH_SIZE    = 32

# ── Hospital Setup ─────────────────────────────────────────
hospitals = [
    ("Hospital A (Mumbai)", df_hospital_A),
    ("Hospital B (Pune)",   df_hospital_B),
    ("Hospital C (Delhi)",  df_hospital_C),
]

# ── Initialize Global Model ────────────────────────────────
global_model = DiagnosticModel(num_classes=2).to(device)
print(f"✅ Global model initialized on {device}")
print(f"📊 Total hospitals: {len(hospitals)}")
print(f"📊 Total patient records: {total} (Data NEVER leaves hospitals!)\n")

# ── Training History ───────────────────────────────────────
history = {
    'round': [], 'global_loss': [], 'global_acc': [],
    'hospital_A_loss': [], 'hospital_B_loss': [], 'hospital_C_loss': [],
}

# ═══════════════════════════════════════════════════════════
#  FEDERATED TRAINING LOOP
# ═══════════════════════════════════════════════════════════
for fl_round in range(1, FL_ROUNDS + 1):
    print(f"\n{'='*60}")
    print(f"  🔄 FEDERATED ROUND {fl_round} / {FL_ROUNDS}")
    print(f"{'='*60}")

    local_models     = []
    num_samples_list = []
    round_losses     = []
    round_accs       = []

    # ── Step 1: Each hospital trains locally ───────────────
    for hospital_name, hospital_df in hospitals:
        local_model, n_samples, loss, acc = train_hospital_node(
            hospital_name   = hospital_name,
            dataframe       = hospital_df,
            img_folder      = img_folder,
            global_model    = global_model,
            epochs          = LOCAL_EPOCHS,
            lr              = LEARNING_RATE,
            batch_size      = BATCH_SIZE,
        )
        local_models.append(local_model)
        num_samples_list.append(n_samples)
        round_losses.append(loss)
        round_accs.append(acc)

    # ── Step 2: Central Aggregator — FedAvg ───────────────
    print(f"\n   🧮 [AGGREGATOR] Running FedAvg across {len(hospitals)} hospital nodes...")
    global_model = fedavg_aggregate(global_model, local_models, num_samples_list)

    # ── Step 3: Compute global weighted metrics ────────────
    total_samples = sum(num_samples_list)
    global_loss = sum(l * n for l, n in zip(round_losses, num_samples_list)) / total_samples
    global_acc  = sum(a * n for a, n in zip(round_accs, num_samples_list)) / total_samples

    # SHA-256 hash for cryptographic audit trail
    model_hash = compute_model_hash(global_model)

    print(f"\n   📊 [GLOBAL MODEL] Round {fl_round} Results:")
    print(f"      Weighted Loss:     {global_loss:.4f}")
    print(f"      Weighted Accuracy: {global_acc:.2f}%")
    print(f"      SHA-256 Hash:      {model_hash[:24]}...")

    # ── Store history ──────────────────────────────────────
    history['round'].append(fl_round)
    history['global_loss'].append(global_loss)
    history['global_acc'].append(global_acc)
    history['hospital_A_loss'].append(round_losses[0])
    history['hospital_B_loss'].append(round_losses[1])
    history['hospital_C_loss'].append(round_losses[2])

print(f"\n{'='*60}")
print("  ✅ FEDERATED TRAINING COMPLETE!")
print(f"  Final Global Accuracy: {history['global_acc'][-1]:.2f}%")
print(f"  Final Global Loss:     {history['global_loss'][-1]:.4f}")
print(f"{'='*60}")
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 11 — Plot Results (Dashboard Charts)              ║
# ╚══════════════════════════════════════════════════════════╝

"""
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor('#0f172a')

for ax in axes:
    ax.set_facecolor('#1e293b')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#334155')

rounds = history['round']

# — Plot 1: Global Model Performance ——————————————————————
axes[0].plot(rounds, history['global_acc'],  'o-', color='#10b981',
             linewidth=2.5, markersize=8, label='Global Accuracy (%)')
axes[0].fill_between(rounds, history['global_acc'],
                     alpha=0.15, color='#10b981')
axes[0].set_title('🌐 Global Model Accuracy (Federated)', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Federated Round', fontsize=11)
axes[0].set_ylabel('Accuracy (%)', fontsize=11)
axes[0].legend(facecolor='#1e293b', labelcolor='white')
axes[0].grid(alpha=0.15)

# — Plot 2: Per-Hospital Loss ——————————————————————————————
axes[1].plot(rounds, history['hospital_A_loss'], 'o-', color='#6366f1',
             linewidth=2, markersize=7, label='Hospital A (Mumbai)')
axes[1].plot(rounds, history['hospital_B_loss'], 's-', color='#0ea5e9',
             linewidth=2, markersize=7, label='Hospital B (Pune)')
axes[1].plot(rounds, history['hospital_C_loss'], '^-', color='#f59e0b',
             linewidth=2, markersize=7, label='Hospital C (Delhi)')
axes[1].plot(rounds, history['global_loss'],    'd-', color='#10b981',
             linewidth=2.5, markersize=8, label='Global Federated Loss', linestyle='--')
axes[1].set_title('🏥 Per-Hospital Training Loss', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Federated Round', fontsize=11)
axes[1].set_ylabel('Loss', fontsize=11)
axes[1].legend(facecolor='#1e293b', labelcolor='white', fontsize=9)
axes[1].grid(alpha=0.15)

plt.suptitle('MediFL — Sr. No. 29 | NIH Chest X-Ray Federated Learning Results',
             color='white', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('medifl_results.png', dpi=150, bbox_inches='tight',
            facecolor='#0f172a')
plt.show()
print("✅ Results chart saved as medifl_results.png")
"""


# ╔══════════════════════════════════════════════════════════╗
# ║  CELL 12 — Save Trained Model & Download                ║
# ╚══════════════════════════════════════════════════════════╝

"""
import os
from google.colab import files

# Save model
os.makedirs('/content/medifl_output', exist_ok=True)
torch.save(global_model.state_dict(), '/content/medifl_output/medifl_global_model.pth')
print("✅ Global model saved!")

# Save training history as JSON
with open('/content/medifl_output/training_history.json', 'w') as f:
    json.dump(history, f, indent=2)
print("✅ Training history saved!")

# Download to your laptop
files.download('/content/medifl_output/medifl_global_model.pth')
files.download('/content/medifl_output/training_history.json')
files.download('medifl_results.png')
print("✅ All files downloaded to your laptop!")
"""

# ============================================================
#  END OF SCRIPT
#  Total Colab Cells: 12
#  Estimated Training Time: ~20-40 min on GPU T4 (free Colab)
# ============================================================
