import re


class gff:
    def __init__(self, gff_name):
        self.gff_name = gff_name
        self.gff_pos = dict()   # annotation to every position chrom/pos => [lt, name]
        self.ann_pos = dict()   # positions for every annotation
        self.readgff(gff_name)  # read GFF file
        self.pos_to_ann()       # make annotation-based dictionary. Keys are ids => [ann, contig, start, stop]

    # read GFF file
    def readgff(self, file):
        print('Read GFF file ' + file)
        gff_file = open(file, 'r')
        gff_content = gff_file.read().split('\n##sequence-region')

        for contig in gff_content[1:]:
            region = re.search('\|?([^\s]+)\s+\d+\s+(\d+)', contig)
            chrom = region.group(1)
            clen = int(region.group(2))
            self.gff_pos[chrom] = list()

            for pos in range(clen + 1):
                self.gff_pos[chrom].append(['', ''])

            items = contig.split('\n')
            # for intergenic space annotations
            prev_pos = 0
            prev_ann = ['', '']
            prev_orient = '+'

            # for annotation of intergenic space near origin
            first_pos = 0
            last_pos = clen
            first_ann = ''
            last_ann = ''
            first_orient = '+'
            last_orient = '+'

            for j in range(1, len(items)):
                fields = items[j].split('\t')

                lt = '-'  # get locus tag
                lt_match = re.search('locus_tag=([^;]+)(;|$)', fields[8])

                if lt_match is not None:
                    lt = lt_match.group(1)

                name = '-'  # get trivial name
                name_match = re.search('gene=([^;]+)(;|$)', fields[8])
                if name_match is not None:
                    name = name_match.group(1)

                # fill positions with information
                for k in range(int(fields[3]), int(fields[4]) + 1):
                    if self.gff_pos[chrom][k][0] is '' and self.gff_pos[chrom][k][0] is '':
                        self.gff_pos[chrom][k] = [lt, name]
                    else:
                        self.gff_pos[chrom][k][0] += ';' + lt
                        self.gff_pos[chrom][k][1] += ';' + name

                # annotate integenic space
                if j > 1 and prev_pos < int(fields[3]):
                    orient1 = 'ds'  # downstream
                    orient2 = 'us'  # upstream

                    if prev_orient is '+':
                        orient1 = 'ds'
                    elif prev_orient is '-':
                        orient1 = 'us'

                    if fields[6] is '-':
                        orient2 = 'ds'
                    elif fields[6] is '+':
                        orient2 = 'us'

                    for k in range(prev_pos + 1, int(fields[3])):
                        self.gff_pos[chrom][k][0] = orient1 + '_' + prev_ann[0] + '<>' + orient2 + \
                                                    '_' + self.gff_pos[chrom][int(fields[3])][0]  # for locus_tag
                        self.gff_pos[chrom][k][1] = orient1 + '_' + prev_ann[1] + '<>' + orient2 + \
                                                    '_' + self.gff_pos[chrom][int(fields[3])][1]  # for gene name

                prev_pos = int(fields[4])
                prev_ann = self.gff_pos[chrom][int(fields[4])]
                prev_orient = fields[6]

                if j == 1:
                    first_pos = int(fields[3])
                    if fields[6] is '+':
                        first_orient = 'us'
                    elif fields[6] is '-':
                        first_orient = 'ds'

                    first_ann = self.gff_pos[chrom][int(fields[3])]
                elif j == len(items) - 1:
                    if fields[6] is '-':
                        last_orient = 'us'
                    elif fields[6] is '+':
                        last_orient = 'ds'

                    last_pos = int(fields[4])
                    last_ann = self.gff_pos[chrom][int(fields[4])]

            # annotate between 1 and first gene
            for j in range(first_pos):
                self.gff_pos[chrom][j][0] = last_orient + '_' + last_ann[0] + '<>' + first_orient + '_' + first_ann[0]
                self.gff_pos[chrom][j][1] = last_orient + '_' + last_ann[1] + '<>' + first_orient + '_' + first_ann[1]

            # annotate between last gene and the end of contig
            for j in range(last_pos, clen + 1):
                self.gff_pos[chrom][j][0] = last_orient + '_' + last_ann[0] + '<>' + first_orient + '_' + first_ann[0]
                self.gff_pos[chrom][j][1] = last_orient + '_' + last_ann[1] + '<>' + first_orient + '_' + first_ann[1]

    # convert gff_pos => ann to ann => pos for locus tags
    # id => locus tag, contig, start, stop
    def pos_to_ann(self):
        print('Convert GFF table')
        ann_id = 0
        for contig in self.gff_pos.keys():
            prev_ann = ''
            self.gff_pos[contig].append(['-', '-'])                             # add one position to the end for
                                                                                # porpose of an algorithm
            for pos in range(len(self.gff_pos[contig]) - 1):
                if prev_ann != self.gff_pos[contig][pos][0]:
                    prev_ann = self.gff_pos[contig][pos][0]
                    if ann_id in self.ann_pos:
                        self.ann_pos[ann_id][3] = pos
                    ann_id += 1
                    self.ann_pos[ann_id] = [self.gff_pos[contig][pos][0], contig, pos, pos]
