# LLM_PM_Tasks — Assessing the Effectiveness of Large Language Models in Project Management

Code, data and results from the MSc dissertation Assessing Effectiveness of Large Language Models in Project Management (Universidade Lusófona, MSc in Computer Science and Information Systems, supervised by Prof. João Caldeira, December 2025).

## What this is about

There is a lot of talk about using LLMs to help project managers, but not much evidence on whether they actually give good answers, or whether an LLM can be trusted to grade another LLM's answer. The study tries to answer three questions:

1. When humans and LLMs both act as judges, how much do they agree with each other?
2. If an LLM is used as a judge, can its scores be trusted?
3. How far can a project manager trust an answer written by an LLM?

## How the study was done

The study used three completed IT infrastructure projects (a sales revenue monitoring application, the migration of a network device discovery application, and an Azure Boards rollout), exported from Microsoft Project to CSV event logs (project ID, task ID, task name, duration, start and finish dates, resource names) which were then used as context in the prompts.

Ten questions of the kind you would ask in a post-project review were then put to each model: were deliverables on time and on budget, what caused the delays, were milestones met, what would you do differently, and so on. Each question was asked per project and once more across all three projects together, and every prompt was repeated five times per model to check how stable the answers are.

The models tested were gpt-3.5-turbo and gpt-4o (OpenAI API) and deepseek-r1, llama3.2 and qwen3 running locally through Ollama.

Every answer was then scored on a 0–3 scale (0 = completely inadequate, 1 = generic, 2 = partially aligned, 3 = fully aligned) by four independent judges: two project managers (one with 5–10 years of experience, one with more than 10 and a PMP certification) and two LLM judges, GPT-4o and GPT-5. Agreement between judges was measured with weighted Cohen's kappa, Kendall's W, Spearman's rho and Krippendorff's alpha, broken down per question, per model and per project.

## What came out of it

The two human judges agreed with each other reasonably well (weighted kappa around 0.74). Humans and LLM judges did not: kappa dropped to around 0.2, and Krippendorff's alpha was negative on most items.

The main reason is that LLM judges are far too generous. Human scores averaged about 1.3 on the 0–3 scale; the LLM judges averaged 2.6–2.8 and put almost everything at 2 or 3, including answers the humans had scored 0 or 1.

The two LLM judges did agree with each other (moderate to substantial kappa), so they are consistent, they are just consistently wrong relative to the experts.

Among the answering models, deepseek-r1 and qwen3 got slightly higher medians from the human judges than gpt-3.5-turbo and llama3.2, but the gap between human and LLM scoring was the same for all of them.

A caveat worth keeping in mind: the judge models and some of the evaluated models come from the same vendor and likely overlap in training data, which may make the judges lean towards answers that look like their own.

In short: LLM answers are useful as a first draft that an experienced project manager still needs to review, and LLM-as-a-judge is a quick, reproducible approximation, not a substitute for expert scoring.

## Repository Contents

| Path | Description |
|------|-------------|
| `Benchmark.py` | Sends each prompt to the selected models and writes the answers to Excel |
| `ChatGPT.py`, `Ollama.py`, `Anthropic.py`, `Google.py`, `Mistral.py`, `HF.py`, `DeepInfra.py` |Small wrappers per LLM provider (only OpenAI and Ollama were used in the study) |
| `query.py`, `convert_csv.py` | Helpers (prompt querying; CSV to XES conversion with pm4py) |
| `projects_questions/` | Prompts: project description + event log + question |
| `projects_answers/` | Raw answers, one file per model, project and question (`<model>_<projectID>_Q<n>.txt`) |
| `projects_judging/` | LLM-as-a-judge outputs for each answer |
| `ul-projects-settings.xlsx`, `ul-projects-settings_judge.xlsx`, `benchmark_settings.xlsx` | Benchmark configuration (models, options, questions) |
| `RC.xlsx`, `RC-New2.xlsx` | Master results files with all answers and judge scores |
| `AI-Evaluation.ipynb`, `AI-Evaluation-New.ipynb`, `Runtime.ipynb` | Notebooks with the agreement metrics and plots |
| `concordance_per_*.tex`, `*.png`, `*.pdf` | Tables and figures used in the study |

## Limitations

Compute was limited, so only a handful of models were tested. All three projects were already finished, so this is a retrospective exercise rather than live project support. The evaluation used a single rubric and a single prompting style, and both LLM judges came from the same vendor. Results may not carry over to newer models or to ongoing projects.

## Citation

```
Abdala Jr., A. J. S. (2025). Assessing Effectiveness of Large Language Models in Project Management.
MSc Dissertation, Universidade Lusófona de Humanidades e Tecnologias, Lisbon.
```
