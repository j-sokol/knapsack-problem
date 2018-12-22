# 🎒 Knapsack Problem

Impelentation using various algorithms of well known knapsack problem.


The algorithms are:

- Bruteforce 
- Simple heuristic
- Dynamic programming
- Branch and bound
- Generic programming

In the end relative error of the heuristic is returned, also program outputs times how long it takes to calculate problem instance.

If you want to see some statistics of how algorithm runs, head to `report/` directory to see jupyter notebooks and latex reports (sadly it's only in czech language).
# How to run

Repository contains testing knapsack data and referential solution data for comparison.

No libraries are needed, only default Python 3.7 instalation.

## Creating virtual environment

```
python3 -m venv __venv__
. ./__venv__/bin/activate
pip install numpy
./run_all.sh
```
or if you want to see genetic algorithm statistics:
```
./run_genetic.sh
```

