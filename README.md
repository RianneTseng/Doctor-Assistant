# 專案進展報告

## 1. 評估指標

DocLens 可評估以下四個數值：

- **Claim Recall**
- **Claim Precision**
- **Citation Recall**
- **Citation Precision**

目前的數據處理僅適用於 **Claim**，因為 **Citation** 需要的數據格式與目前處理的數據不相符。

### Claim 的計算方式
- Claim 是透過 `result` 來生成多條 **subclaim**，再將 **subclaim** 餵給 LLM 來評分。
- **general_subclaim_generation.json** 負責生成 **subclaim**，`Prompt` 如下：
```
{
"role": "system",
"content": "Instruction: You are a helpful medical assistant. Read the clinical report and generate at least __MIN_CLAIM__ at most __MAX_CLAIM__ short claims that are supported by the clinical report. Each short claim should contain only one fact. The generated claims should cover all facts in the clinical report."
}
```
- **general_claim_entail.json** 負責計算 **claim recall** 和 **claim precision**，`Prompt` 如下：
```
{
"role": "system",
"content": "Instruction: You are a helpful medical assistant. Please evaluate whether the clinical report can fully entail each claim below. Also generate an explanation for your answer. Please output '1' or '0' for each claim, where '1' means the claim can be fully entailed by the clinical_report, and '0' means the claim contains information that cannot be entailed by the clinical_report."
}
```

### Citation 的計算方式
- 在生成 `output` 時，將對話的 `index` 記錄到每一句診斷中。
- 之後透過 **acibench-test1-gpt-4-shot2-quick_test3.json** 和 **acibench-test1-gpt-4-shot2-quick_test3.citation_score** 來評估 citation 是否正確。例如：

```
{
"example_id": "D2N107",
"input": "
    [0][doctor] so bryan it's nice to see you again in the office today what's going on
    [1][patient] i was in my yard yesterday and i was raking leaves and i felt fine and then when i got into my house about two hours later my back started tightening up and i started getting pins and needles in my right foot
    [2][doctor] alright have you ever had this type of back pain before
    [3][patient] i had it once about three years ago but it went away after a day
    [4][doctor] okay and did you try anything for the pain yet did you take anything or have you have you tried icing
    [5][patient] put some ice on it and i tried two advils and it did n't help..."
"output": "
    CHIEF COMPLAINT

    Back pain and tingling sensation in the right foot [1].

    HISTORY OF PRESENT ILLNESS

    Bryan is a 62-year-old male presented with significant complaints of back pain after raking leaves in his yard [1][5]..."
}
```

其中 `[1][5]` 的 citation 記錄了該診斷的來源對話 index，這些 index 會在 **acibench-test1-gpt-4-shot2-quick_test3.citation_score** 中進一步評估是否正確。


## 2. 服務選擇與調整

- DocLens 原先使用 **Azure OpenAI** 服務，而非 OpenAI 本身的服務。
- 選擇 **Azure OpenAI** 是基於其安全性考量，但模型部屬較為困難。
- 因此，我將 Azure 服務改為 **OpenAI**，並調整了部分程式碼。
- 主要修改的檔案包括：
  - **Python 檔案**：
    - `generate_subclaims.py`（負責生成 subclaim，改用 OpenAI API）
    - `run_entailment.py`（負責評估 claim entailment，改用 OpenAI API）
  - **Shell Script 檔案**：
    - `eval_general_claim_generation.sh`（執行 subclaim 生成的流程）
    - `eval_general_model_citation.sh`（評估 citation 的 script）


## 3. OpenAI 模型測試

- 目前測試過 **GPT-4o Mini** 和 **GPT-4o**。
- **Claim Recall** 和 **Claim Precision** 的計算方式：
  - 需先透過 `general_subclaim_generation.json` 生成 **subclaim**。
  - 再使用 `general_claim_entail.json` 計算 **claim recall** 與 **claim precision**。
- 測試結果如下：
  - **GPT-4o Mini**:
    - Claim Recall: 0.6667
    - Claim Precision: 0.4375
  - **GPT-4o**:
    - Claim Recall: 0.5333
    - Claim Precision: 0.3529
- 測試過程中發現，生成的分數波動較大，有時甚至可能出現 `0` 的狀況。
- 我認為這是因為：
  - 目前的對話數據中，並非所有資料都足以產生 `subclaim`。
  - `general_claim_entail.json` 的 prompt 設計可能不夠詳細，導致評估結果存在較大變異。


## 4. 測試數據轉換工具

- 撰寫了一個 `csv2json.py` 腳本，用於將目前的測試數據從 **CSV** 轉換為 **JSON**。
- 生成兩種 JSON 檔案：
  - **data.json**：用來放在 `/data`，對應到 `$REFERENCE`，僅包含 `input`、`reference`、`example_id`。
  - **results.json**：用來放在 `/results`，對應到 `$SAVENAME`，包含 `input`、`output`、`reference`、`example_id`。
- **JSON 欄位對應關係：**
  - `example_id`：來自 CSV 讀取到的 index。
  - `input`：由 `prev_step_str`（如果有）加上 `synthesis_question` 組合而成。
  - `output`：來自 CSV 欄位 `system_response`。
  - `reference`：對應 CSV 欄位 `ground_truth_answer`，

    在 **ACI-Bench-TestSet-1\_clean.json** （由 DocLens 提供的資料）`reference` 可能是由真實的醫生撰寫的醫療紀錄，而 `output` 是由 LLM 根據 `input` 生成的醫療紀錄。例如：

```
"example_id": "D2N107",
"reference": "
    CHIEF COMPLAINT
    
    Low back pain.
    
    HISTORY OF PRESENT ILLNESS
    
    Bryan Brooks is a pleasant 39-year-old male who presents to the clinic today for the evaluation of low back pain. He is accompanied today by his partner.
    
    Approximately 2 hours after he finished raking leaves yesterday, the patient began to feel a tightening sensation in his low back and tingling in his right foot. Prior to this, he recalls a similar episode approximately 3 years ago in which his symptoms resolved after 1 day. Ice and Advil provided no relief, but his pain is less severe when he is in a seated position and taking a hot shower helped alleviate his pain. The patient's partner reports that his pain seems to worsen when he stands up.
    
    REVIEW OF SYSTEMS
    
    Musculoskeletal: Reports low back pain.
    Neurological: Reports tingling in the right foot.
    
    PHYSICAL EXAM
    
    NEURO: Normal strength and sensation.
    MSK: Examination of the lumbar spine: No pain on extension. Some pain with flexion. Pain with palpation around L5. Dorsiflexion is normal. Pulses are equal in all extremities.
    
    RESULTS
    
    X-rays obtained and reviewed in office today were normal.
    
    ASSESSMENT
    
    Low back sprain.
    
    PLAN
    
    The examination findings and x-ray results were discussed with the patient and his partner today. I recommend we treat this conservatively with rest, meloxicam, and formal physical therapy. If he fails to improve, we can consider obtaining an MRI for further evaluation.
    
    INSTRUCTIONS
    
    The patient will follow up in 2 weeks.",
"output": "
    CHIEF COMPLAINT
    
    Back pain and tingling sensation in the right foot [1].
    
    HISTORY OF PRESENT ILLNESS
    
    Bryan is a 62-year-old male presented with significant complaints of back pain after raking leaves in his yard [1][5].
    The patient reports that he was in his yard and was raking leaves which was when he started to feel the tightening in his back and later started to experience a tingling sensation in his right foot[1][5].
    The patient reports that he was in his yard and was raking leaves which was when he started to feel the tightening in his back and later started to experience a tingling sensation in his right foot[1][5].
    He experienced similar symptoms about three years ago, but it resolved after a day [3].
    He attempted to resolve his current pain by resting, using ice, and taking Advil, but this did not result in any relief [5][6].
    Patient reports that the only time he feels some relief from the pain is when he is in a hot shower or sits [7][8].
    
    REVIEW OF SYSTEMS
    
    ...
    
    PHYSICAL EXAMINATION
    
    ...
    
    RESULTS
    
    ...
    
    ASSESSMENT AND PLAN
    
    ..."
```

