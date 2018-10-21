#!/bin/bash

mkdir csvs



for i in 4 10 15 20 22 25 27 30 32 35 37 40;
do 
	echo "+ ./src/knapsack-problem.py -e ./data/instance/knap_${i}.inst.dat  ./data/solution/knap_${i}.sol.dat"
	./src/knapsack-problem.py -e ./data/instance/knap_${i}.inst.dat  ./data/solution/knap_${i}.sol.dat >> csvs/error_${i}.csv
done

for i in 4 10 15 20 22 25 27 30 32 35 37 40;
do 
	echo "+ ./src/knapsack-problem.py -s ./data/instance/knap_${i}.inst.dat  ./data/solution/knap_${i}.sol.dat"
	./src/knapsack-problem.py -s ./data/instance/knap_${i}.inst.dat  ./data/solution/knap_${i}.sol.dat >> csvs/speed_${i}.csv
done


error_csvs = `ls csvs/error_*`
speed_csvs = `ls csvs/speed_*`

paste -d ',' "$error_csvs" >> csvs/all_errors.csv
paste -d ',' "$speed_csvs" >> csvs/all_speeds.csv