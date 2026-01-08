N=1
L=3600
echo $N > fort.11
echo $L > fort.10 

gfortran add.f90 -o add.x

i=21150
while [ $i -le 21155 ]
do
cp Pt-$i.pdos fort.12
./add.x
i=$((i+50))
done
mv fort.13 Pt.MAV


i=21150
while [ $i -le 21155 ]
do
cp watB-$i.pdos fort.12
./add.x
i=$((i+50))
done
mv fort.13 watB.MAV


i=21150
while [ $i -le 21155 ]
do
cp ion-$i.pdos fort.12   
./add.x
i=$((i+50))   
done 
mv fort.13 ion.MAV     


