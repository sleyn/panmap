import glob
import gff
import sys
import getopt
import numpy as np

try:
    opts, args = getopt.getopt(sys.argv[1:], "r:g:c:t:")      # reference fasta, gff file, contig for template
except getopt.GetoptError:
    print("add_alignment_core.py -r <reference.fna> -g <reference.gff> -c <Contig name> -t <Threshold>")
    sys.exit(1)

for opt, arg in opts:
    if opt == '-r':
        reference_fasta = arg
    elif opt == '-g':
        reference_gff = arg
    elif opt == '-c':
        template_contig = arg
    elif opt == '-t':
    	threshold = float(arg)

print('Start generating alignment')
aln = open("alignment.aln", 'w')     # output alignment
region_file = open("regions.txt", 'w')      # region was taken for alignment or not

#read reference
ref = open(reference_fasta,'r')         # read reference DNA fasta
ref_gff = gff.gff(reference_gff)        # make class for gff file of the reference
ref_gff.readgff()
ref_gff.pos_to_ann()
ref_content = ref.read().splitlines()
fasta = ''.join(ref_content[1:])
fasta = list(fasta)
ref.close()
alignment_array = np.empty(len(fasta), dtype ='uint8')   # initialize array
alignment_names = []                    # list of names
delete_mask = np.ones(len(fasta), dtype=bool)       # array for removal the regions
number_of_genomes = float(0)                   # number of aligned genomes
k = 0

#read snp and coords (to introduce unaligned parts) files
snp_files = glob.glob("*.snps")
for snp_file_name in snp_files:
    k += 1
    print(str(k) + ": Add " + snp_file_name)
    new_fasta = np.array(fasta, dtype='c')
    snp_file = open(snp_file_name,'r')
    print("Introduce SNP")
    for snp in snp_file.readlines()[5:-1]:          # introduse SNPs
        snp_prop = snp.split()
        if snp_prop[1] == '.':                      # do not introduce insertions in the reference
            continue
        if snp_prop[2] == '.':
            snp_prop[2] = '-'
        elif snp_prop[2] not in list('ATGCNatgcn-'):
            snp_prop[2] = 'N'
        new_fasta[int(snp_prop[0]) - 1] = snp_prop[2]

    gap = np.zeros(len(new_fasta), dtype=bool)           # array representing gap positions as False
    print("Read coord")
    coords_file = open(snp_file_name[:-4] + 'coords','r')
    for coord in coords_file.readlines()[5:]:
        coords_prop = coord.split()
        for pos in range(int(coords_prop[0]) - 1, int(coords_prop[1])):
            gap[pos] = True

    print("Introduce gaps")
    for pos in range(len(gap)):
        if gap[pos] == False:
            new_fasta[pos] = '-'

    print("Collect genome name")
    alignment_names.append(snp_file_name[:-5])
    print("Append genome to alignment")
    alignment_array = np.vstack((alignment_array, new_fasta.view(np.uint8)))
    number_of_genomes += 1.0

alignment_array = alignment_array[1:,:]

for locus, params in ref_gff.ann_pos[template_contig].items():
    print("Checking locus " + ' '.join([str(x) for x in params]))
    if params[1] != template_contig:
        continue
    region_len = 0.0
    sum_of_gaps = 0.0
    for i in range(params[2] - 1, params[3]):
        sum_of_gaps_col = 0.0           # sum of gaps in the column
        region_len += 1.0
        col = alignment_array[:,i]
        unique, counts = np.unique(col, return_counts=True)
        count_dict = dict(zip(unique, counts))
        if 45 in count_dict:
            sum_of_gaps_col += count_dict[45]

        if sum_of_gaps_col / number_of_genomes >= threshold:
            sum_of_gaps += 1

    if sum_of_gaps / region_len >= threshold:
        delete_mask[range(params[2] - 1, params[3])] = False
        region_file.write(params[0] + '\t' + str(int(region_len)) + '\t-' + '\t' + str(round(sum_of_gaps / region_len, 2)) + '\n')
    else:
        region_file.write(params[0] + '\t' + str(int(region_len)) + '\t+' + '\t' + str(round(sum_of_gaps / region_len, 2)) + '\n')

region_file.close()
alignment_array = alignment_array[:,delete_mask]

for j in range(int(number_of_genomes)):
    aln.write(">"+alignment_names[j]+"\n")
    new_fasta_str = [''.join([chr(nuc) for nuc in alignment_array[j,i:i + 60]]) for i in range(0, alignment_array.shape[1], 60)]
    aln.write('\n'.join(new_fasta_str)+"\n")

aln.close()

print('Done')