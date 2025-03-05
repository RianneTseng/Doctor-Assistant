import argparse
import os
import json
import time
from tqdm import tqdm
from copy import deepcopy
import numpy as np
import re

import openai
from openai import OpenAIError

client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))

SECTION_DIVISIONS = ['subjective', 'objective_exam', 'objective_results', 'assessment_and_plan']

def remove_citations(sent):
    return re.sub(r"\[\d+", "", re.sub(r" \[\d+", "", sent)).replace(" |", "").replace("]", "")

def completion_with_backoff(**kwargs):
    is_ok = False
    retry_count = 0
    while not is_ok:
        retry_count += 1
        try:
            response = client.chat.completions.create(**kwargs)
            is_ok = True
        except openai.RateLimitError as error:
            if retry_count <= 30:
                if retry_count % 10 == 0:
                    print(f"OpenAI API retry for {retry_count} times ({error})")
                time.sleep(10)
                continue
            else:
                return {}
        except openai.BadRequestError as error:
            if 'maximum context length' in error._message:
                if retry_count <= 3:
                    print(f"reduce max_tokens by 500")
                    kwargs['max_tokens'] = kwargs['max_tokens'] - 500
                    continue
                else:
                    print(error)
                    return {}
            else:
                print(error)
                return {}
        except Exception as error:
            print(error)
            return {}
    return response

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # data
    parser.add_argument('--result_file', required=True, help='filename of the system-generated outputs.')
    parser.add_argument("--dataset_name", type=str, default=None, help="Name of the dataset")

    # evaluation setting
    parser.add_argument("--mode", type=str, default="claim_recall", choices=['claim_recall','claim_precision','same'])
    parser.add_argument("--use_persection_claims", action="store_true", default=False, help="Generate claims for each section")

    # evaluation model
    parser.add_argument('--prompt_file', required=True, help='filename of the prompt dict .json.')
    parser.add_argument("--max_new_tokens", type=int, default=2000, help="Max number of new tokens to generate in one step")

    args = parser.parse_args()

    result_file, dataset_name, mode, prompt_file, max_new_tokens = args.result_file, args.dataset_name, args.mode, args.prompt_file, args.max_new_tokens

    EVALUATOR_NAME = "gpt-4o-2024-08-06"

    if mode == 'claim_recall':
        savefile = result_file.replace('.json', '.claim_scores')
    elif mode == 'claim_precision':
        savefile = result_file.replace('.json', '.output_claim_scores')
    elif mode == 'same':
        assert dataset_name == 'meqsum'
        savefile = result_file.replace('.json', '.same_scores')

    if not args.use_persection_claims:
        SECTION_DIVISIONS = ['full']

    output_data = json.load(open(result_file, 'r'))

    print(f"Saving scores to {savefile.split('/')[-1]}..")

    if os.path.exists(savefile):
        print('Save file exist!')
        claims_score = json.load(open(savefile))
    else:
        claims_score = {section: {str(x['example_id']): [] for x in output_data} for section in SECTION_DIVISIONS}

    prompt_template = json.load(open(prompt_file, 'r'))
    for i in range(1, len(prompt_template)-1):
        prompt_template[i]['content'] = json.dumps(prompt_template[i]['content'])

    TEXT_NAME = {'acibench': 'clinical_note', 'mimic': 'radiology_report'}

    wrong_format_count = 0
    new_generation_count = 0
    for section in SECTION_DIVISIONS:
        text_name = TEXT_NAME.get(dataset_name, "clinical_report")

        if mode == 'claim_recall':
            text_key = f'output_{section}' if args.use_persection_claims else 'output'
            subclaim_key = f'subclaims_reference_{section}' if args.use_persection_claims else 'subclaims_reference'
        elif mode == 'claim_precision':
            text_key = f'reference_{section}' if args.use_persection_claims else 'reference'
            subclaim_key = f'subclaims_output_{section}' if args.use_persection_claims else 'subclaims_output'
        elif mode == 'same':
            text_key = 'output'
            subclaim_key = 'reference'

        for item in output_data:
            eid_str = str(item['example_id'])
            text = remove_citations(item.get(text_key, ""))
            claims = item.get(subclaim_key, [])

            if not claims:
                claims_score[section][eid_str] = []
                continue
            
            if not text:
                claims_score[section][eid_str] = [{"claim": claim, "entailment_prediction": 0} for claim in claims]
                continue
            
            if len(claims_score[section][eid_str]) == len(claims):
                continue
            
            print('Do not exist:', section, eid_str)
            prompt = deepcopy(prompt_template)
            prompt[-1]['content'] = json.dumps({text_name: text, "claims": claims})

            response = completion_with_backoff(
                model=EVALUATOR_NAME, messages=prompt, max_tokens=max_new_tokens
            )

            new_generation_count += 1

            try:
                judgment_dict = json.loads(response.choices[0].message.content)
                claims_score[section][eid_str] = judgment_dict
            except:
                print('CANNOT CONVERT TO JSON')
                wrong_format_count += 1

            if new_generation_count % 5 == 0:
                print('Saving results..')
                json.dump(claims_score, open(savefile, 'w'), indent=4, sort_keys=True)

    json.dump(claims_score, open(savefile, 'w'), indent=4, sort_keys=True)
    print(f"WRONG FORMAT COUNT: {wrong_format_count}")