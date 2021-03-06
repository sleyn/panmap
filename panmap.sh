for i in `cat genome_list.txt`
do
#    i=${i#..\/}
#    i=${i%.fna}
    echo "Alignment for $i"
    nucmer --prefix=$i reference.fna fna/$i.fna
    delta-filter -r -q $i.delta > $i.filter
    show-snps -Clr $i.filter > $i.snps
    show-coords -k -r $i.filter > $i.coords
    rm $i.delta
    rm $i.filter
done

python3 panmap.py -r reference.fna -g reference.gff -c $1 -t $2
