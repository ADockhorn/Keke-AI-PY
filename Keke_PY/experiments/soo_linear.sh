#!/bin/bash

#SBATCH --job-name=KekeSingleObjectiveOptimizationTest          # Name unter dem der Job in der Job-History gespeichert wird
#SBATCH --mail-user=rongero@tnt.uni-hannover.de
#SBATCH --mail-type=ALL               # Eine Mail wird bei Job-Start/Ende versendet
#SBATCH --partition=cpu_short_stud
#             later cpu_long_stud (?)

#SBATCH --array=0-0                   # Es werden 5 Tasks mit den IDs von 0-4 gestartet
#SBATCH --cpus-per-task=1
#             later max 20
#SBATCH --mem-per-cpu=1G
#               later 4G
#SBATCH --time=00:20:00
#        later 06:00:00
#SBATCH --output=soo_test_1_%A_%a-out.txt   # Logdatei für den merged STDOUT/STDERR output (%A wird durch slurm Job-ID ersetzt und %a durch den Array Index)


# setup conda, and a conda-environment like environment.txt :
#source setup_on_my_laptot.sh
source setup_on_cluster.sh



# Change to my work dir
# SLURM_SUBMIT_DIR is an environment variable that automatically gets
# assigned the directory from which you did submit the job. A batch job
# is like a new login, so you'll initially be in your HOME directory.
# So it's usually a good idea to first change into the directory you did
# submit your job from.
cd $SLURM_SUBMIT_DIR

python Keke_PY/experiments/test_all_soo.py --argument $SLURM_ARRAY_TASK_ID



# Load the modules you need, see corresponding page in the cluster documentation
#module load my_modules

# Start my serial app
# srun is needed here only to create an entry in the accounting system,
# but you could also start your app without it here, since it's only serial.
#srun ./my_serial_app