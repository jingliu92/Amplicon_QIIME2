

# QIIME 2 16S rRNA Sequencing Analysis Pipeline

---

## Before You Start
Before running the pipeline, ensure you have the following prepared:

### 1. FASTQ Files
- **Format**: Paired-end or single-end FASTQ files generated from your sequencing platform (e.g., Illumina).
- **Organization**: Store the files in a directory, ensuring each file follows the naming convention:  
  `<sample-ID>_L001_R1_001.fastq.gz` for forward reads and `<sample-ID>_L001_R2_001.fastq.gz` for reverse reads (if paired-end).
- Example directory structure:
  ```
  raw_data/
  ├── sample1_L001_R1_001.fastq.gz
  ├── sample1_L001_R2_001.fastq.gz
  ├── sample2_L001_R1_001.fastq.gz
  ├── sample2_L001_R2_001.fastq.gz
  ```

---

### 2. Metadata File
- A tab-delimited `.tsv` file with required columns:
  - `#SampleID`: Matches filenames of FASTQ files.
  - Experimental metadata (e.g., `Group`, `Treatment`).
- Example:
  ```
  #SampleID    Group    Treatment
  sample1      Control  None
  sample2      Treated  DrugA
  ```
- Validate using the [QIIME 2 Metadata Validator](https://qiime2.org/metadata/).

---

### 3. Download Database
Use a pre-trained classifier compatible with your sequencing region (e.g., SILVA, Greengenes).  
- **SILVA**:
  ```bash
  wget https://data.qiime2.org/2021.2/common/silva-138-99-nb-classifier.qza
  ```
- **Greengenes**:
  ```bash
  wget https://data.qiime2.org/2021.2/common/gg-13-8-99-nb-classifier.qza
  ```
- **UNITE (for fungal ITS)**:
  ```bash
  wget https://data.qiime2.org/2021.2/common/unite-ver8-99-classifier-01.12.2021.qza
  ```

---

## Logging on to the HPC Server
If using a high-performance computing (HPC) server for QIIME 2 analysis:

### 1. Access the Server
- Log in to your HPC server using SSH:
  ```bash
  ssh <username>@<hpc-server-address>
  ```
  Example:
  ```bash
  ssh jdoe@hpc.university.edu
  ```

- If required, load the QIIME 2 module or activate the environment:
  ```bash
  module load qiime2/2021.2
  ```
  Or, if using Conda:
  ```bash
  conda activate qiime2-2021.2
  ```

---

## Setting up the Working Directory
Create and organize your working directory for hands-on analysis:
1. **Create a New Directory**:
   ```bash
   mkdir ~/qiime2_analysis
   cd ~/qiime2_analysis
   ```

2. **Organize Subdirectories**:
   ```bash
   mkdir raw_data metadata results temp
   ```
   - `raw_data/`: Store your FASTQ files.
   - `metadata/`: Store your metadata file (e.g., `metadata.tsv`).
   - `results/`: Save all analysis outputs.
   - `temp/`: Use for intermediate files during the pipeline.

3. **Upload Files to the Server**:
   Use `scp` or `rsync` to upload your raw data and metadata file:
   ```bash
   scp /local/path/to/raw_data/* <username>@<hpc-server-address>:~/qiime2_analysis/raw_data/
   scp /local/path/to/metadata.tsv <username>@<hpc-server-address>:~/qiime2_analysis/metadata/
   ```

4. **Verify Files**:
   List the uploaded files to ensure everything is in place:
   ```bash
   ls -R ~/qiime2_analysis
   ```

---

## Pipeline Workflow

### 1. Input Preparation
- Import raw sequencing data:
  ```bash
  qiime tools import \
    --type 'SampleData[PairedEndSequencesWithQuality]' \
    --input-path raw_data/ \
    --input-format CasavaOneEightSingleLanePerSampleDirFmt \
    --output-path demux-paired-end.qza
  ```

---

### 2. Quality Control
#### Step 2.1: Visualize Sequencing Quality
```bash
qiime demux summarize \
  --i-data demux-paired-end.qza \
  --o-visualization demux-summary.qzv
```

#### Step 2.2: Trim and Denoise with DADA2
```bash
qiime dada2 denoise-paired \
  --i-demultiplexed-seqs demux-paired-end.qza \
  --p-trim-left-f 0 \
  --p-trim-left-r 0 \
  --p-trunc-len-f 250 \
  --p-trunc-len-r 250 \
  --o-table feature-table.qza \
  --o-representative-sequences rep-seqs.qza \
  --o-denoising-stats denoising-stats.qza
```

---

### 3. Taxonomic Classification
#### Step 3.1: Assign Taxonomy
```bash
qiime feature-classifier classify-sklearn \
  --i-classifier silva-138-99-nb-classifier.qza \
  --i-reads rep-seqs.qza \
  --o-classification taxonomy.qza
```

#### Step 3.2: Visualize Taxonomy
```bash
qiime metadata tabulate \
  --m-input-file taxonomy.qza \
  --o-visualization taxonomy.qzv
```

---

### 4. Diversity Analysis
#### Generate Diversity Metrics
```bash
qiime diversity core-metrics-phylogenetic \
  --i-phylogeny rooted-tree.qza \
  --i-table feature-table.qza \
  --p-sampling-depth 10000 \
  --m-metadata-file metadata/metadata.tsv \
  --output-dir core-metrics-results
```

---

### 5. Visualization
#### Taxonomic Bar Plots
```bash
qiime taxa barplot \
  --i-table feature-table.qza \
  --i-taxonomy taxonomy.qza \
  --m-metadata-file metadata/metadata.tsv \
  --o-visualization taxa-bar-plots.qzv
```

---

### 6. Differential Abundance Analysis
#### Perform Differential Abundance Testing with ANCOM
```bash
qiime composition add-pseudocount \
  --i-table feature-table.qza \
  --o-composition-table comp-table.qza
```

```bash
qiime composition ancom \
  --i-table comp-table.qza \
  --m-metadata-file metadata/metadata.tsv \
  --m-metadata-column Treatment \
  --o-visualization ancom-results.qzv
```

---

### 7. Export Results
#### Export Feature Table and Taxonomy
```bash
qiime tools export \
  --input-path feature-table.qza \
  --output-path exported-feature-table
```

```bash
qiime tools export \
  --input-path taxonomy.qza \
  --output-path exported-taxonomy
```

---

### 8. Wrap Up
Deactivate the QIIME 2 environment:
```bash
conda deactivate
```

This pipeline provides a comprehensive, step-by-step guide for analyzing 16S rRNA data using QIIME 2. Adjust parameters as needed based on your dataset.
