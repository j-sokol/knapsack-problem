#!/bin/bash


for i in 4 10 15 20 22 25 27 30 32 35 37 40;
do 
	echo "+ ./src/exact-method.py ./data/instance/knap_${i}.inst.dat  ./data/solution/knap_${i}.sol.dat"
	./src/exact-method.py ./data/instance/knap_${i}.inst.dat  ./data/solution/knap_${i}.sol.dat >> size_${i}.log
done