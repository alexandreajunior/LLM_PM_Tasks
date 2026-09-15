# LLM_PM_Tasks — Assessing the Effectiveness of Large Language Models in Project Management

Code, data and results supporting the MSc dissertation **"Assessing Effectiveness of Large Language Models in Project Management"** (Alexandre José Silva Abdala Jr., Universidade Lusófona, MSc in Computer Science and Information Systems, adviser: Prof. João Caldeira, December 2025).

## Overview

Large language models (LLMs) are increasingly proposed as assistants for project managers, but their reliability — both as *answer generators* and as *judges* of other models' answers — is largely untested in this domain. This study asks two questions:

1. How well do LLMs answer everyday project management questions when given real project event logs?
2. How closely do LLM-based judges (LLM-as-a-judge) align with experienced human project managers when scoring those answers on a shared rubric?

## Methodology

- **Projects:** three completed IT-infrastructure projects (a sales-performance application, a network device discovery migration, and an Azure Boards implementation). Microsoft Project files were exported to CSV event logs (project ID, task ID, task name, duration, start/finish dates, resource names) and embedded in the prompts as context.
- **Questions:** ten questions typical of a completed-project review (e.g. on-time/on-budget delivery, causes of delays, adherence to plan, resource usage, milestones, lessons learned), asked per project and across all three projects together.
- **Evaluated models:** `gpt-3.5-turbo` and `gpt-4o` (OpenAI, online) and `deepseek-r1`, `llama3.2` and `qwen3` (run locally via Ollama). Each question was repeated five times per model to measure response consistency.
- **Judges:** two human project managers (5–10 and 10+ years of experience, one PMP-certified) and two LLM judges (GPT-4o and GPT-5). All judges scored every answer independently on a 0–3 rubric (0 = completely inadequate, 1 = generic, 2 = partially aligned, 3 = fully aligned).
- **Agreement analysis:** Weighted Cohen's kappa, Kendall's W, Spearman's rho and Krippendorff's alpha, computed per question, per model and per project.

## Key Findings

- **Humans agree with each other far more than they agree with LLMs.** Human–human weighted kappa was around 0.74, versus roughly 0.2 for human–LLM pairs; Krippendorff's alpha was negative for most human–LLM comparisons.
- **LLM judges are systematically lenient.** Human mean scores were around 1.3 on the 0–3 scale, while LLM judges averaged 2.6–2.8, compressing almost all ratings into the 2–3 range even where humans scored 0 or 1.
- **LLM judges are consistent with each other but not with experts.** LLM–LLM agreement was substantial, indicating reproducible behaviour, yet this internal consistency did not translate into alignment with human judgement.
- **DeepSeek and Qwen stood out** among the evaluated models with distinct performance profiles.
- **Possible training-data bias.** Judge and evaluated models may share overlapping training data (and in some cases the same vendor), which may lead LLM judges to favour similarly trained models.

**Bottom line:** LLMs can serve as fast, reproducible first-pass assistants for project management questions, but they should not replace expert human judgement — as answerers or as judges — without calibration and human oversight.

## Repository Contents

| Path | Description |
|------|-------------|
| `Benchmark.py` | Main driver that sends each question/prompt to the selected models and saves answers to Excel |
| `ChatGPT.py`, `Ollama.py`, `Anthropic.py`, `Google.py`, `Mistral.py`, `HF.py`, `DeepInfra.py` | Thin wrappers for each LLM engine (only OpenAI and Ollama were used in the study) |
| `query.py`, `convert_csv.py` | Helper scripts (prompt querying; CSV → XES event-log conversion with pm4py) |
| `projects_questions/` | Prompts: project description + event log + question |
| `projects_answers/` | Raw answers per model, project and question (`<model>_<projectID>_Q<n>.txt`) |
| `projects_judging/` | LLM-as-a-judge outputs for each answer |
| `ul-projects-settings.xlsx`, `ul-projects-settings_judge.xlsx`, `benchmark_settings.xlsx` | Benchmark configuration (models, options, questions) |
| `RC.xlsx`, `RC-New2.xlsx` | Master results files with all answers and judge scores |
| `AI-Evaluation.ipynb`, `AI-Evaluation-New.ipynb`, `Runtime.ipynb` | Analysis notebooks (agreement metrics, plots) |
| `concordance_per_*.tex`, `*.png`, `*.pdf` | Generated tables and figures used in the dissertation |

## Limitations

Limited computational resources restricted the number of models tested; all projects were already completed (retrospective analysis); the evaluation was offline rather than embedded in live workflows; a single rubric and prompting strategy were used; and both LLM judges came from the same vendor.

## Citation

```
Abdala Jr., A. J. S. (2025). Assessing Effectiveness of Large Language Models in Project Management.
MSc Dissertation, Universidade Lusófona de Humanidades e Tecnologias, Lisbon.
```
