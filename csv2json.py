import pandas as pd
import json
import re

# Function to generate and save two JSON files based on DataFrame content
def generate_full_and_partial_json(df):
    full_results = []
    partial_results = []
    for i, row in df.iterrows():
        # Initialize dialogue sequence
        dialogue_sequence = []

        # If there is a previous step string, add it to the sequence
        prev_steps = ""
        if pd.notna(row['prev_step_str']):
            pattern = r'(使用者回應)'
            prev_steps = re.sub(pattern, '[user]', row['prev_step_str'])
            pattern = r'(系統回覆)'
            prev_steps = re.sub(pattern, '[system]', prev_steps)

        # Format the input with user and system tags
        formatted_input = prev_steps + "[user]" + row['synthesis_question']

        # Full data entry with output included
        full_entry = {
            "example_id": f"D2N{i+1:03}",
            "reference": row['ground_truth_answer'],
            "input": formatted_input.strip(),
            "output": row['system_response']
        }
        full_results.append(full_entry)
        
        # Partial data entry without output
        partial_entry = {
            "example_id": f"D2N{i+1:03}",
            "reference": row['ground_truth_answer'],
            "input": formatted_input.strip()
        }
        partial_results.append(partial_entry)
    
    # Save full results to a JSON file
    full_json_path = 'evaluation_results.json'
    with open(full_json_path, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, ensure_ascii=False, indent=4)
    
    # Save partial results to a JSON file
    partial_json_path = 'evaluation_data.json'
    with open(partial_json_path, 'w', encoding='utf-8') as f:
        json.dump(partial_results, f, ensure_ascii=False, indent=4)

    return full_json_path, partial_json_path

# Load your DataFrame
data = pd.read_csv('GPT4o v.s. LLaMA - o3utput.csv')

# Generate the JSON files
full_json_path, partial_json_path = generate_full_and_partial_json(data)

print(f"Result JSON file saved at: {full_json_path}")
print(f"Data JSON file saved at: {partial_json_path}")
