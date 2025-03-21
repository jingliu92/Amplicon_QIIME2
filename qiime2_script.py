import subprocess
import os
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define a function to run QIIME 2 commands
def run_command(cmd):
    print("Running: " + " ".join(cmd))
    subprocess.run(cmd, check=True)

# Define argument parser
def parse_args():
    parser = argparse.ArgumentParser(description='QIIME2-based 16S/ITS Analysis Pipeline')
    parser.add_argument('--sample-folder', required=True, help='Path to folder containing sample FASTQ files')
    parser.add_argument('--metadata-file', required=True, help='Path to metadata file (mapping file)')
    parser.add_argument('--database', required=True, help='Path to trained QIIME2 classifier')
    parser.add_argument('--output-dir', required=True, help='Path to output directory')
    parser.add_argument('--paired-end', action='store_true', help='Use paired-end reads instead of single-end')
    return parser.parse_args()

# Function to generate a QIIME 2 manifest file
def generate_manifest(sample_folder, paired_end):
    manifest_path = os.path.join(sample_folder, "manifest.csv")
    with open(manifest_path, "w") as manifest:
        manifest.write("sample-id,absolute-filepath,direction\n")

        fastq_files = sorted([f for f in os.listdir(sample_folder) if f.endswith('.fastq.gz')])
        sample_dict = {}

        for f in fastq_files:
            if "_R1_" in f:
                sample_id = f.split("_R1_")[0]
                direction = "forward"
            elif "_R2_" in f:
                sample_id = f.split("_R2_")[0]
                direction = "reverse"
            else:
                continue

            if sample_id not in sample_dict:
                sample_dict[sample_id] = {}
            sample_dict[sample_id][direction] = os.path.abspath(os.path.join(sample_folder, f))

        for sample_id, paths in sample_dict.items():
            if paired_end and "forward" in paths and "reverse" in paths:
                manifest.write(f"{sample_id},{paths['forward']},forward\n")
                manifest.write(f"{sample_id},{paths['reverse']},reverse\n")
            elif not paired_end and "forward" in paths:
                manifest.write(f"{sample_id},{paths['forward']},forward\n")
    return manifest_path


# Function to generate basic information summary
def generate_basic_info(output_dir):
    stats_file = os.path.join(output_dir, 'stats.qza')

    # Export and read DADA2 stats
    stats_tsv = os.path.join(output_dir, 'exported_stats', 'stats.tsv')
    run_command(['qiime', 'tools', 'export', '--input-path', stats_file, '--output-path', os.path.join(output_dir, 'exported_stats')])
    stats_data = pd.read_csv(stats_tsv, sep='\t')

    # Create summary table
    summary_data = {
        "Sample ID": stats_data['sample-id'],
        "Total Reads": stats_data['input'],
        "Total Reads Retained": stats_data['filtered']
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(os.path.join(output_dir, "basic_info_summary.tsv"), sep='\t', index=False)

# Function to generate taxonomy summary tables
def generate_taxonomy_tables(output_dir, level, name):
    collapsed_table = os.path.join(output_dir, f'collapsed-table-{name}.qza')
    exported_table = os.path.join(output_dir, 'exported_data', f'feature-table-{name}.tsv')

    # Collapse taxonomy at the specified level
    collapse_cmd = [
        'qiime', 'taxa', 'collapse',
        '--i-table', os.path.join(output_dir, 'table.qza'),
        '--i-taxonomy', os.path.join(output_dir, 'taxonomy.qza'),
        '--p-level', str(level),
        '--o-collapsed-table', collapsed_table
    ]
    run_command(collapse_cmd)

    # Export taxonomy table
    export_cmd = [
        'qiime', 'tools', 'export',
        '--input-path', collapsed_table,
        '--output-path', os.path.join(output_dir, 'exported_data')
    ]
    run_command(export_cmd)

    if os.path.exists(exported_table):
        taxonomy_data = pd.read_csv(exported_table, sep='\t', skiprows=[1])
        taxonomy_data["Proportion"] = taxonomy_data.iloc[:, 1:].div(taxonomy_data.iloc[:, 1:].sum(axis=0), axis=1) * 100
        taxonomy_data.to_csv(os.path.join(output_dir, f"taxonomy_summary_{name}.tsv"), sep='\t', index=False)

# Function to generate pie charts
def generate_pie_charts(data, output_dir):
    os.makedirs(os.path.join(output_dir, "pie_charts"), exist_ok=True)

    for sample in data.columns[1:]:  # Skip taxonomy column
        sample_data = data[["Feature ID", sample]].dropna()
        sample_data[sample] = sample_data[sample].astype(float)
        sample_data = sample_data[sample_data[sample] > 0]

        # Select top 15 most abundant taxa
        sample_data = sample_data.sort_values(by=sample, ascending=False)
        if len(sample_data) > 15:
            top_15 = sample_data.head(15)
            other = pd.DataFrame({"Feature ID": ["Other"], sample: [sample_data[sample][15:].sum()]})
            sample_data = pd.concat([top_15, other])

        labels = [f"{taxon} ({abundance:.1f}%)" for taxon, abundance in zip(sample_data["Feature ID"], sample_data[sample] / sample_data[sample].sum() * 100)]

        plt.figure(figsize=(8, 8))
        plt.pie(sample_data[sample], labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(f"Taxonomic Composition of {sample}")
        plt.savefig(os.path.join(output_dir, "pie_charts", f"{sample}_pie_chart.png"))
        plt.close()

# Main processing function
def process_samples(args):
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate manifest file
    manifest_path = generate_manifest(args.sample_folder, args.paired_end)

    # Step 1: Import FASTQ files as a QIIME 2 artifact
    import_cmd = [
        'qiime', 'tools', 'import',
        '--type', 'SampleData[PairedEndSequencesWithQuality]' if args.paired_end else 'SampleData[SequencesWithQuality]',
        '--input-path', manifest_path,
        '--input-format', 'PairedEndFastqManifestPhred33' if args.paired_end else 'SingleEndFastqManifestPhred33',
        '--output-path', os.path.join(args.output_dir, 'demux-paired.qza' if args.paired_end else 'demux-single.qza')
    ]
    run_command(import_cmd)

    # Step 2: Perform quality control and denoising using DADA2
    denoise_cmd = [
        'qiime', 'dada2', 'denoise-paired' if args.paired_end else 'denoise-single',
        '--i-demultiplexed-seqs', os.path.join(args.output_dir, 'demux-paired.qza' if args.paired_end else 'demux-single.qza'),
        '--p-trunc-len-f', '230' if args.paired_end else '250',
        '--p-trunc-len-r', '200' if args.paired_end else '0',
        '--o-table', os.path.join(args.output_dir, 'table.qza'),
        '--o-representative-sequences', os.path.join(args.output_dir, 'rep-seqs.qza'),
        '--o-denoising-stats', os.path.join(args.output_dir, 'stats.qza')
    ]
    run_command(denoise_cmd)

    # Generate taxonomy summary tables for Genus, Family, and Phylum
    for level, name in [(6, "Genus"), (5, "Family"), (3, "Phylum")]:
        generate_taxonomy_tables(args.output_dir, level, name)

    # Generate basic information table
  generate_basic_info(args.output_dir)

    # Generate pie charts
    taxonomy_tsv = os.path.join(args.output_dir, 'exported_data', 'feature-table-Genus.tsv')
    if os.path.exists(taxonomy_tsv):
        taxonomy_data = pd.read_csv(taxonomy_tsv, sep='\t', skiprows=[1])
        generate_pie_charts(taxonomy_data, args.output_dir)

    print("Analysis complete. Pie charts and summary saved in:", args.output_dir)

if __name__ == "__main__":
    args = parse_args()
    process_samples(args)
