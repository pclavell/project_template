#!/bin/bash


################################## README BEFORE USAGE ##################################

# ERROR: a first argument needs to be chosen between the following:
#    -run: to start an execution 
#    -rerun: for failed runs that blocked the dir, runs unlock 
#    -dryrun: tests pipeline structure and makes dag 
# Usage: bash submit_smk.sh {run|rerun|dryrun}

############ --------------------------------------------------------------- ############


module load miniconda && source activate sqanti3-snakemake

PARAM="$1"

case "$PARAM" in
  run)
    snakemake \
      -s Snakefile \
      -j 250 \
      --configfile ../../resources/config.yml \
      --directory "$PWD" \
      --keep-going \
      --latency-wait 120 \
      --rerun-incomplete \
      --cluster "sbatch \
        -q gp_bscls \
        -c {resources.threads} \
        -A bsc83 \
        -o smk_logs/{wildcards.sample}/%j_%x.out \
        -t {resources.runtime}"
    ;;
  rerun)
    snakemake --unlock \
      -s Snakefile \
      -j 250 \
      --configfile ../../resources/config.yml \
      --directory "$PWD" \
      --keep-going \
      --latency-wait 120 \
      --rerun-incomplete \
      --cluster "sbatch \
        -q gp_bscls \
        -c {resources.threads} \
        -A bsc83 \
        -o smk_out/{wildcards.sample}/%j_%x.out \
        -t {resources.runtime}"
    ;;
  dryrun)
    snakemake \
      -s Snakefile \
      -j 250 \
      --dag \
      --configfile ../../resources/config.yml \
      --directory "$PWD" \
      --keep-going \
      --latency-wait 120 \
      --rerun-incomplete \
      --cluster "sbatch \
        -q gp_bscls \
        -c {resources.threads} \
        -A bsc83 \
        -o smk_out/{wildcards.sample}/%j_%x.out \
        -t {resources.runtime}" \
      -n
    ;;
  graph)
    snakemake \
      -s Snakefile \
      -j 250 \
      --dag \
      --configfile ../../resources/config.yml \
      --directory "$PWD" \
      --keep-going \
      --latency-wait 120 \
      --rerun-incomplete \
      --cluster "sbatch \
        -q gp_bscls \
        -c {resources.threads} \
        -A bsc83 \
        -o smk_out/{wildcards.sample}/%j_%x.out \
        -t {resources.runtime}" \
      -n \
      | dot -Tpng > "workflow_dag.png"
    ;;
  *)
    echo -e "ERROR: a first argument needs to be chosen between the following:\n \
      -run: to start an execution \n \
      -rerun: for failed runs that blocked the dir, runs unlock \n \
      -dryrun: tests pipeline structure \n \
      -graph: makes DAG png \
      \nUsage: bash $0 {run|rerun|dryrun}"
    exit 1
    ;;
esac


