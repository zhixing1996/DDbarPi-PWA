#! /bin/bash
  
######## Part 1 #########
# Script parameters     #
#########################
 
# Specify the partition name from which resources will be allocated, mandatory option
#SBATCH --partition=gpu
 
# Specify the QOS, mandatory option
#SBATCH --qos=normal
 
# Specify which group you belong to, mandatory option
# This is for the accounting, so if you belong to many group,
# write the experiment which will pay for your resource consumption
#SBATCH --account=gpupwa
  
# Specify your job name, optional option, but strongly recommand to specify some name
#SBATCH --job-name=RES
  
# Specify how many cores you will need, default is one if not specified
#SBATCH --ntasks=2
  
# Specify the output file path of your job
# Attention!! Your afs account must have write access to the path
# Or the job will be FAILED!
#SBATCH --output=/hpcfs/bes/gpupwa/jingmq/job_output/gpujob-%j.out
  
# Specify memory to use, or slurm will allocate all available memory in MB
#SBATCH --mem-per-cpu=2048
  
# Specify how many GPU cards to use
#SBATCH --gres=gpu:v100:1

#SBATCH --time=48:00:00
    
######## Part 2 ######
# Script workload    #
######################
  
# Replace the following lines with your real workload
  
# list the allocated hosts
srun -l hostname
  
# list the GPU cards of the host
/usr/bin/nvidia-smi -L
echo "Allocate GPU cards : ${CUDA_VISIBLE_DEVICES}"
  
cd PATH
mkdir -p fit_result
rm -f fit_result/*json
for i in {1..500}
do
    python fit.py
    mv final_params.json ./fit_result/final_params_${i}.json
done
