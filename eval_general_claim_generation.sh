SAVENAME=$1
REFERENCE=$2
PROMPT_FILE=${3:-"claim_evaluation/prompts/general_subclaim_generation.json"}

# generate reference subclaims
python3 claim_evaluation/generate_subclaims.py --eval_file data/${REFERENCE}.json \
    --result_file results/${SAVENAME}.json \
    --mode reference_claims \
    --prompt_file $PROMPT_FILE

# generate output subclaims
python3 claim_evaluation/generate_subclaims.py --eval_file data/${REFERENCE}.json \
    --result_file results/${SAVENAME}.json \
    --mode output_claims \
    --prompt_file $PROMPT_FILE
