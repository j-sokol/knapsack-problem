#!/bin/bash

mkdir -p csvs/genetic

for xp in 0.1 0.2 0.3 0.4 0.5 0.6 0.8; do
	./src/knapsack-problem.py -m genetic -a compare -xp=${xp} -mp=0.1 -ec=10 -tc=16 -tps=2 -ge=1000 inst.dat >> csvs/genetic/xover_probability_${xp}.csv
	sed -i "1s/^.*/generation,best_combination_xp_${xp}/" csvs/genetic/xover_probability_${xp}.csv
done


for mp in 0.01 0.025 0.05 0.1 0.15 0.2 0.3; do
	./src/knapsack-problem.py -m genetic -a compare -xp=0.4 -mp=${mp} -ec=10 -tc=16 -tps=2 -ge=1000 inst.dat >> csvs/genetic/mutation_probability_${mp}.csv
	sed -i "1s/^.*/generation,best_combination_mp_${mp}/" csvs/genetic/mutation_probability_${mp}.csv
done


for ec in 1 2 3 4 5 7 10 20 30 50; do
	./src/knapsack-problem.py -m genetic -a compare -xp=0.4 -mp=0.1 -ec=${ec} -tc=16 -tps=2 -ge=1000 inst.dat >> csvs/genetic/elitism_count_${ec}.csv
	sed -i "1s/^.*/generation,best_combination_ec_${ec}/" csvs/genetic/elitism_count_${ec}.csv
done

for tc in 1 2 5 10 16 20 40 50; do
	./src/knapsack-problem.py -m genetic -a compare -xp=0.4 -mp=0.1 -ec=10 -tc=${tc} -tps=2 -ge=1000 inst.dat >> csvs/genetic/tournament_count_${tc}.csv
	sed -i "1s/^.*/generation,best_combination_tc_${tc}/" csvs/genetic/tournament_count_${tc}.csv
done

for tps in 1 2 5 10 16 20 40 50; do
	./src/knapsack-problem.py -m genetic -a compare -xp=0.4 -mp=0.1 -ec=10 -tc=16 -tps=${tps} -ge=1000 inst.dat >> csvs/genetic/tournament_pool_size_${tps}.csv
	sed -i "1s/^.*/generation,best_combination_tps_${tps}/" csvs/genetic/tournament_pool_size_${tps}.csv
done

for ge in 50 100 200 500 1000 1200 1500; do
	./src/knapsack-problem.py -m genetic -a compare -xp=0.4 -mp=0.1 -ec=10 -tc=16 -tps=2 -ge=${ge} inst.dat >> csvs/genetic/generations_${ge}.csv
	sed -i "1s/^.*/generation,best_combination_ge_${ge}/" csvs/genetic/generations_${ge}.csv
done
