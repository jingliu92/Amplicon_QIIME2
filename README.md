
# QIIME 2 Pipeline

## File Description
- **Readme.md**: Introduction to the QIIME 2 Pipeline.  
- **install.Rmd**: Step-by-step tutorial for installation.  
- **pipeline.sh**: Command-line analysis script for Linux (Slurm environment).  
- **data/**: Folder containing example raw sequencing data.  
- **result/**: Folder containing example result data.  
- **visualization/R.Rmd**: Interactive diversity analysis in R, with outputs in a reproducible HTML format.  
- **figures/**: Folder containing examples of generated figures.  

---

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

## Installing QIIME 2
Follow the step-by-step tutorial in [install.md](https://github.com/jingliu92/Amplicon_QIIME2/blob/main/install.md) for detailed installation instructions.  

For additional details, refer to the official QIIME 2 website: [QIIME 2 Installation Guide](https://docs.qiime2.org/2024.10/install/).  
