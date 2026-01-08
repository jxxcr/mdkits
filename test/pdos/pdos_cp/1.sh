#!/bin/bash

PROJECT=pdos

k1=O
k2=H
k3=Pt
k4=Ne
k5=Li

gfortran pdos.f90 -o pdos.x
#gfortran-4.6 filter.f90 -o filter.x

i=21150
while [ $i -le 21155 ]
do


tail -n +3 ./${PROJECT}-k1-$i.cube > tmp.pdos
awk '{print $2*27.2114, $4+$5+$6+$7}' tmp.pdos > input.pdos
./pdos.x
mv output.pdos ${k1}.pdos
awk '{print $1,$2}' ${k1}.pdos > ${k1}-$i.pdos

tail -n +3 ./${PROJECT}-k2-$i.cube > tmp.pdos
awk '{print $2*27.2114, $4}' tmp.pdos > input.pdos
./pdos.x
mv output.pdos ${k2}.pdos
awk '{print $1,$2}' ${k2}.pdos > ${k2}-$i.pdos

tail -n +3 ./${PROJECT}-k3-$i.cube > tmp.pdos 
awk '{print $2*27.2114, $8+$9+$10+$11+$12}' tmp.pdos > input.pdos
./pdos.x
mv output.pdos ${k3}.pdos
awk '{print $1,$2}' ${k3}.pdos > ${k3}-$i.pdos

tail -n +3 ./${PROJECT}-k5-$i.cube > tmp.pdos
awk '{print $2*27.2114, $4}' tmp.pdos > input.pdos
./pdos.x
mv output.pdos ${k5}.pdos
awk '{print $1,$2}' ${k5}.pdos > ${k5}-$i.pdos


 
#water pdos

pr -m -t -e100 ${k2}-$i.pdos ${k1}-$i.pdos > watB.input
awk '{print $1, $2+$4}' watB.input > watB-$i.pdos

pr -m -t -e100 ${k3}-$i.pdos > Pt.input
awk '{print $1, $2}' Pt.input > Pt-$i.pdos

pr -m -t -e100 ${k5}-$i.pdos > ion.input
awk '{print $1, $2}' ion.input > ion-$i.pdos

    i=$((i+50))

      done

#awk '{print $1,$3}' ${k5}.pdos > tot.pdos
