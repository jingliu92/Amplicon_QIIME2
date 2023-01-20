# Meta_analysis_NE

# Data Set 1 (SRP159781)
V3-V4 region were amplified using primers 338F (5' ACTCCTACGGGAGGCAGCAG 3') and 806R (5' GGACTACHVGGGTWTCTAAT 3')
CN
SRR7801859 SRR7801858 SRR7801861 SRR7801860 SRR7801863 SRR7801862
CP
SRR7801849 SRR7801850 SRR7801847 SRR7801848 SRR7801851 SRR7801852

Only use forword sequence 
Import seq data to qiime2 extract V4 region
```
qiime tools import \
  --type 'SampleData[SequencesWithQuality]' \
  --input-path sample_list.txt \
  --output-path Output/3_demux.qza \
  --input-format SingleEndFastqManifestPhred33V2

qiime demux summarize \
  --i-data Output/3_demux.qza \
  --o-visualization Output/3_demux.qzv

qiime cutadapt trim-single \
  --i-demultiplexed-sequences Output/3_demux.qza \
  --p-cores 16 \
  --p-front-f GTGCCAGCMGCCGCGGTAA \
  --p-front-r GGACTACHVGGGTWTCTAAT \
  --p-match-adapter-wildcards \
  --p-match-read-wildcards \
  --p-discard-untrimmed \
  --p-no-indels \
  --p-overlap 10 \
  --o-trimmed-sequences Output/3_trim.qza \
  --verbose 
  
  qiime cutadapt trim-single \
  --i-demultiplexed-sequences Output/3_demux.qza \
  --p-cores 16 \
  --p-front GTGCCAGCMGCCGCGGTAA \
  --p-adapter GGACTACHVGGGTWTCTAAT \
  --p-match-adapter-wildcards \
  --p-match-read-wildcards \
  --p-discard-untrimmed \
  --p-no-indels \
  --p-overlap 10 \
  --o-trimmed-sequences Output/3_trim.qza \
  --verbose 
  
  qiime demux summarize \
  --i-data Output/3_trim.qza \
  --o-visualization Output/3_trim.qzv
  
```
qiime tools import \
  --type 'SampleData[PairedEndSequencesWithQuality]' \
  --input-path sample_list.txt \
  --input-format PairedEndFastqManifestPhred33 \
  --output-path Output/raw_data.qza

# Visualize the raw dataset
qiime demux summarize \
  --i-data Output/raw_data.qza \
  --o-visualization Output/raw_data.qzv
  
 qiime cutadapt trim-paired \
  --i-demultiplexed-sequences Output/raw_data.qza \
  --p-cores 16 \
  --p-front-f ACTCCTACGGGAGGCAGCAG \
  --p-front-r GGACTACHVGGGTWTCTAAT \
  --p-match-adapter-wildcards \
  --p-match-read-wildcards \
  --p-no-indels \
  --p-overlap 10 \
  --o-trimmed-sequences Output/data_trim.qza \
  --verbose
  
  qiime demux summarize \
  --i-data Output/data_trim.qza \
  --o-visualization Output/data_trim.qzv
  ### Clean data
  
  qiime vsearch join-pairs \
  --i-demultiplexed-seqs Output/data_trim.qza \
  --o-joined-sequences  Output/data_joined.qza \
  --verbose
  
  qiime demux summarize \
 --i-data Output/data_joined.qza \
 --o-visualization Output/data_joined.qzv
  ```
