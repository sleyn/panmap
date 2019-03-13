for i in `cat genome_list.txt`
do
    i=${i#..\/}
    i=${i%.fna}
    echo "Alignment for $i"
    ~/ngsbin/MUMmer3.23/nucmer --prefix=$i reference.fna ../$i.fna
    ~/ngsbin/MUMmer3.23/delta-filter -r -q $i.delta > $i.filter
    ~/ngsbin/MUMmer3.23/show-snps -Clr $i.filter > $i.snps
    ~/ngsbin/MUMmer3.23/show-coords -k -r $i.filter > $i.coords
    rm $i.delta
    rm $i.filter
done

python3 add_alignment_core.py -r reference.fna -g reference.gff -c LT571449