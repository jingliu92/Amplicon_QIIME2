
# Tutorial: Installing QIIME 2 Using Conda

This tutorial walks you through the steps to install **QIIME 2 Core 2021.2** distribution natively using the **Miniconda** package manager. QIIME 2 is a powerful tool for microbiome data analysis but cannot currently run on Windows directly. For Windows users, a virtual machine is recommended for learning purposes or for small datasets (fewer than 100 samples).

---

## Prerequisites
- **Linux (64-bit)** or **macOS (64-bit)** system  
- **Miniconda** package manager installed (no administrative privileges required)

---

## 1. Installing Miniconda

1. **Download the latest Miniconda installer**:  
   ```bash
   wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   ```

2. **Run the installer**:  
   ```bash
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

3. **Follow the installation prompts**:
   - Press **ENTER** to proceed through the license agreement.
   - Type **yes** to accept the license terms.
   - Confirm the default installation directory (e.g., `~/miniconda3`) or specify a custom directory.  
   - Type **yes** to initialize Miniconda (`conda init`).

4. **Remove the installer** (optional):  
   ```bash
   rm Miniconda3-latest-Linux-x86_64.sh
   ```

5. **Activate Miniconda** (if not automatically initialized):  
   ```bash
   source ~/.bashrc
   ```

---

## 2. Optional: Configure Conda for Faster Downloads

To speed up downloads, you can add frequently used channels and configure a mirror for faster installations (e.g., Tsinghua University mirror for users in China):

```bash
conda config --add channels defaults
conda config --add channels conda-forge
conda config --add channels bioconda
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda
```

Update Conda to the latest version:  
```bash
conda update conda
```

Install additional tools, such as `wget` for downloading files:  
```bash
conda install -y wget
```

---

## 3. Installing QIIME 2 with Conda

1. **Download the QIIME 2 installation file**:  
   For Linux:
   ```bash
   wget -c https://data.qiime2.org/distro/amplicon/qiime2-amplicon-2024.10-py310-linux-conda.yml
   ```

   For macOS:
   ```bash
   wget -c https://data.qiime2.org/distro/amplicon/qiime2-amplicon-2024.10-py310-osx-conda.yml
   ```

2. **Create a Conda environment for QIIME 2**:  
   ```bash
   conda env create -n qiime2-2024.10 --file qiime2-2021.2-py36-linux-conda.yml
   ```

   This step may take some time, depending on your network speed, as it installs all dependencies.

3. **Activate the environment**:  
   ```bash
   conda activate qiime2-2024.10
   ```

---

## 4. Testing the Installation

To check if QIIME 2 is installed correctly, run:  
```bash
qiime --help
```

You should see the QIIME 2 command-line interface (q2cli) help menu. This confirms a successful installation.

---

## 5. Managing the Environment

- To deactivate the QIIME 2 environment when not in use:  
  ```bash
  conda deactivate
  ```

- To remove an old version of QIIME 2:  
  ```bash
  conda env remove -n qiime2-<version>
  ```

---

## 6. Updating QIIME 2

QIIME 2 does not support in-place upgrades. To install a new version, create a new Conda environment using the steps above, specifying the appropriate version.

---

## Notes:
- For large-scale datasets, ensure that you have sufficient computational resources or consider deploying QIIME 2 on a high-performance computing cluster.  
- Refer to the [QIIME 2 Documentation](https://docs.qiime2.org) for additional details and tutorials.  

By following these steps, you’ll have QIIME 2 set up and ready to analyze your 16S rRNA gene sequencing data!

