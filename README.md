
# QIIME 2 Pipeline
---
A comprehensive tutorial for 16S amplicon sequencing data analysis, covering every step from raw sequencing data processing to results visualization and statistical analysis. This repository includes step-by-step instructions for quality control, taxonomic classification, diversity analysis, and generating publication-ready visualizations using QIIME 2 and complementary tools.

## File Description
- **Readme.md**: Introduction to the QIIME 2 Pipeline.  
- **install.md**: Step-by-step tutorial for installation.  
- **pipeline.sh**: Command-line analysis script for Linux (Slurm environment).  
- **data/**: Folder containing example raw sequencing data.  
- **result/**: Folder containing example result data.  
- **visualization/R.md**: Interactive diversity analysis in R, with outputs in a reproducible HTML format.  
- **figures/**: Folder containing examples of generated figures.  

---

## Installing QIIME 2
Follow the step-by-step tutorial in [install.md](https://github.com/jingliu92/Amplicon_QIIME2/blob/main/install.md) for detailed installation instructions.  

For additional details, refer to the official QIIME 2 website: [QIIME 2 Installation Guide](https://docs.qiime2.org/2024.10/install/).  

## Workflow for Analyzing 16S rRNA Data in QIIME 2
1. **Input Preparation**  
   - Import raw sequencing data (FASTQ files) along with sample metadata into the QIIME 2 framework.  

2. **Quality Control**  
   - Perform read quality filtering, trimming, and denoising using tools like DADA2 or Deblur to generate high-quality representative sequences and feature tables.  

3. **Taxonomic Classification**  
   - Assign taxonomy to Operational Taxonomic Units (OTUs) or Amplicon Sequence Variants (ASVs) using reference databases such as SILVA, Greengenes, or GTDB.  

4. **Diversity Analysis**  
   - Evaluate **alpha diversity** (within-sample metrics, e.g., Shannon Index) and **beta diversity** (between-sample metrics, e.g., Bray-Curtis dissimilarity) to explore community structure and differences.  

5. **Visualization**  
   - Generate intuitive plots, such as taxonomic composition plots, rarefaction curves, and PCoA plots for diversity analysis.  

6. **Statistical Testing**  
   - Conduct differential abundance testing to identify taxa associated with specific conditions or treatments.  

---
# Data Analysis
## Logging on to the HPC Server
If using a high-performance computing (HPC) server for QIIME 2 analysis:

### 1. Access the Server
- Log in to your HPC server using SSH:
  ```
  ssh <username>@<hpc-server-address>
  ```
  Example:
  ```
  ssh jliu@hpc.university.edu
  ```
---

## Setting up the Working Directory
Create and organize your working directory for hands-on analysis:
1. **Create a New Directory**:
   ```
   mkdir ProjectName
   cd ProjectName
   ```
2. **Organize Subdirectories**:
   ```
   mkdir raw_data metadata results temp
   ```
   - `raw_data/`: Store your FASTQ files.
   - `metadata/`: Store your metadata file (e.g., `metadata.tsv`).
   - `results/`: Save all analysis outputs.
   - `temp/`: Use for intermediate files during the pipeline.

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
  sample2      Treated  Trt1
  ```
---

### 3. **Download Database** 
**Available Databases for 16S rRNA Taxonomy Classification** (Choose one based on your analysis requirements and preferences)
- **SILVA** (Last updated: July 2024):
  ```
  # Download reference sequence file
  wget https://www.arb-silva.de/no_cache/download/archive/release_138_2/Exports/SILVA_138.2_SSURef_tax_silva.fasta.gz
  
  # Download reference taxonomy file
  wget https://www.arb-silva.de/no_cache/download/archive/release_138_2/Exports/taxonomy/tax_slv_ssu_138.2.txt.gz
  ```
- **Greengenes2** (Last updated:Sep.2024):
  ```
  wget https://ftp.microbio.me/greengenes_release/current/2024.09.seqs.fna.gz
  wget https://ftp.microbio.me/greengenes_release/current/2024.09.taxonomy.asv.tsv.gz
  ```
- **RDP** (Last updated:Aug.2023):
  ```
  wget https://sourceforge.net/projects/rdp-classifier/files/RDP_Classifier_TrainingData/RDPClassifier_16S_trainsetNo19_QiimeFormat.zip
  ```

---

### Upload Files to the Server**:
   Use `scp` or `globus` to upload your raw data and metadata file:
   ```
   scp /local/path/to/raw_data/* <username>@<hpc-server-address>:~/qiime2_analysis/raw_data/
   scp /local/path/to/metadata.tsv <username>@<hpc-server-address>:~/qiime2_analysis/metadata/
   ```

---
## Active QIIME2
- Load the QIIME 2 module if it's already installed in the HPC.
  ```
  module avail # 
  module load qiime2
  ```
- Or, if using Conda:
  ```
  conda activate qiime2-2024.10
  ```

## Pipeline Workflow

### 1. Input Preparation
- Create a manifest file to import FASTQ files into QIIME2
- Navigate to the directory containing the fastq.gz files
```
cd /path/to/fastq/files
# Create the header for the manifest file
echo "sample-id,absolute-filepath,direction" > manifest.csv
# Add forward reads to the manifest file
for i in *_R1_001.fastq.gz; do 
    echo "${i/_S*/},$PWD/$i,forward" >> manifest.csv
done

# Add reverse reads to the manifest file
for i in *_R2_001.fastq.gz; do 
    echo "${i/_S*/},$PWD/$i,reverse" >> manifest.csv
done
# Replace underscores in sample IDs with dots (optional, for formatting consistency)
awk 'BEGIN{FS=OFS=","} {gsub(/_/, ".", $1); print}' manifest.csv > manifest_cleaned.csv

# Verify the manifest file
cat manifest_cleaned.csv
```

- Import raw sequencing data (paired-end):
  ```
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

