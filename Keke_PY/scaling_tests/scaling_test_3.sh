#!/bin/bash

#SBATCH --job-name=KekeScalingTestCpus3          # Name unter dem der Job in der Job-History gespeichert wird
#SBATCH --mail-user=rongero@tnt.uni-hannover.de
#SBATCH --mail-type=ALL               # Eine Mail wird bei Job-Start/Ende versendet
#SBATCH --partition=cpu_short_stud
#             later cpu_long_stud (?)

#SBATCH --array=0-0                   # Es werden 5 Tasks mit den IDs von 0-4 gestartet
#SBATCH --cpus-per-task=3
#             later max 20
#SBATCH --mem-per-cpu=1G
#               later 4G
#SBATCH --time=01:00:00
#        later 06:00:00
#SBATCH --output=scaling_test_3_cpus_%A_%a-out.txt   # Logdatei für den merged STDOUT/STDERR output (%A wird durch slurm Job-ID ersetzt und %a durch den Array Index)


# setup conda, and a conda-environment like environment.txt :
#source setup_on_my_laptop.sh
source setup_on_cluster.sh

cd $SLURM_SUBMIT_DIR

python Keke_PY/scaling_tests/scaling_test.py 3
