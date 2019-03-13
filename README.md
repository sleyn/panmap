# panmap

**panmap** is a wrapper for nucmer that can create multifasta of whole genome alignment by mapping multiple close related genomes on a reference. panmap could make core genome alignment by filtering genome regions with gap fraction above threshold. To create alignment panmap:
1. Searchs SNPs between query and refrence genomes with nucmer.
2. Searchs which parts of the reference genome that are missing in the query genome.
3. Incorporates differences into the reference nucleotide sequence.
4. For each genomic region (continious region of the genome with the same annotation based on GFF file) panmap calculates if the region should be keept for core or removed. This is desided by two steps:
    1. For each position if fraction of gaps is greater than a threshold, then position considered as a gapped.
    2. For all positions in a region if fraction of gapped positions is greater that a threshold than region is a subject for removal.

## Installation

```
git clone https://github.com/sleyn/panmap.git
```

#### Dependences:

* *nucmer* - should be in the $PATH

  [Installation guidelines](https://github.com/mummer4/mummer/blob/master/INSTALL.md)
  
* *numpy* python package

  [Installation guidelines](https://www.scipy.org/scipylib/download.html)
  
## Usage

Prepare reference nucleotide Fasta. Current version allows to map genomes only to one contig. Choose the appropriate contig and genome. Preferntially use chromosome of a complete genome.

Prepare GFF file for this contig in PATRIC/PROKKA style. Example:
```
##gff-version 3
##sequence-region LT571449 1 2793003
LT571449	Prodigal:2.6	CDS	1	1356	.	+	0	ID=fig_1282.1900_00001;Name=dnaA;gene=dnaA;inference=ab initio prediction:Prodigal:2.6,similar to AA sequence:UniProtKB:P68866;locus_tag=fig_1282.1900_00001;product=Chromosomal replication initiator protein DnaA
LT571449	Prodigal:2.6	CDS	1665	2798	.	+	0	ID=fig_1282.1900_00002;eC_number=2.7.7.7;Name=dnaN;gene=dnaN;inference=ab initio prediction:Prodigal:2.6,similar to AA sequence:UniProtKB:P99103;locus_tag=fig_1282.1900_00002;product=DNA polymerase III subunit beta
LT571449	Prodigal:2.6	CDS	3231	3467	.	+	0	ID=fig_1282.1900_00003;inference=ab initio prediction:Prodigal:2.6;locus_tag=fig_1282.1900_00003;product=hypothetical protein
LT571449	Prodigal:2.6	CDS	3464	4579	.	+	0	ID=fig_1282.1900_00004;Name=recF_1;gene=recF_1;inference=ab initio prediction:Prodigal:2.6,similar to AA sequence:UniProtKB:P9WHI9;locus_tag=fig_1282.1900_00004;product=DNA replication and repair protein RecF
LT571449	Prodigal:2.6	CDS	4590	6521	.	+	0	ID=fig_1282.1900_00005;eC_number=5.99.1.3;Name=gyrB;gene=gyrB;inference=ab initio prediction:Prodigal:2.6,similar to AA sequence:UniProtKB:Q6GKU0;locus_tag=fig_1282.1900_00005;product=DNA gyrase subunit B
```

prepare *fna* folder with .fna fasta files for genomes that you want to map.

prepare 'genome_list.txt' file with list of genome IDs. IDs should be the same as .fna file names. Example:
```
1155135.3
1213731.3
1000590.6
```

The work folder structure should be following:
```
.
..
[fna]               # folder with fna files
reference.fna       # fasta of the reference contig
reference.gff       # gff file for the reference contig
genome_list.txt     # genomes IDs (names of fna files witout extension) - made for the case if you want to subset genomes

```

Run *panmap.sh* with the name of refeence contig.
```
./panmap.sh <Reference contig name> <Threshold>
```
