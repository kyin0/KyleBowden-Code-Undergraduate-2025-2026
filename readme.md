# Welcome to my 2025-2026 Dissertation code. 

## User Manual

### Setting Up the Pipeline

Before running experiments, ensure that the strategy config is set correctly, and Ollama is running locally with the desired model installed. The configuration file is located at config/config.yml.

### Example Configuration

```
llm:
  MODEL: qwen2.5-coder:32b
  TEMPERATURE: 0.1
  TOP_K: 20
  TOP_P: 0.8
  SEED: 42
  TIMEOUT_SECONDS: 900
  LLM_ENDPOINT: http://localhost:11434/api/generate
  REPEAT_PENALTY: 1.05
  REPEAT_LAST_N: 128
  NUM_PREDICT: 1000

rag:
  ENABLED: True
  RAG_N: 4

runner:
  MAX_REPAIR_ITERATIONS: 6
  TIMEOUT: 10

store:
  DB_NAME: dissertation
```

Ensure `LLM_ENDPOINT` points to your local Ollama instance.

### Environment Variables
Create a `.env` file with

```.env
DATABASE_KEY=mongodb+srv://... # your MongoDB connection string
```

### Database Setup
Your MongoDB database must include two collections:
- `experiments`
- `tasks`

Task Schema:
```json
{
  "_id": "YOUR TASK ID",
  "v": 1,
  "description": "YOUR DESCRIPTION HERE",
  "created_at": "CURRENT TIMESTAMP"
}
```

You can insert it manually, or use `insert_task.py`, edit the values, and run.

### Running Experiments

Two options:

First, use `python run_experiment.py` in terminal (ensure task IDs are in the file)

Or,

You can programmatically use 
```py
Orchestrator().run_experiment("task_id")
```

### Results

Results are automatically saved to the `experiments` collection on MongoDB.

### Predefined Tasks

Available at: `setup/dissertation.tasks.json`

## Maintenance Manual

You can get the code from https://github.com/kyin0/KyleBowden-Code-Undergraduate-2025-2026 and download from there.

Python 3.12 is recommended. 

To install dependencies, you can use `pip install -r requirements.txt`.

### System Requirements
Depends on mondel size. For larger models (e.g., `qwen2.5-coder:32b`), you will need 8+ cores CPU, 32-64GB RAM, and ideally 8GB of GPU VRAM.

### Ollama Setup

Download https://ollama.com/download

Commands:

- `ollama pull [model]`
- `ollama run [model]`
- `ollama list`
- `ollama rm [model]`

### MongoDB Setup

Download https://www.mongodb.com/try/download/community. 

### RAG 

To add new RAG chunks, you can add files to `knowledge/maspy/chunks/` and update `knowledge/maspy/index.json` to register them. Entries in the `index.json` file should be in the form:

```json
{
  "id": "CHUNK_ID",
  "path": "chunks/CHUNK_PATH",
  "source": "SOURCE",
  "title": "TITLE",
  "tags": ["tag1", "tag2", "tag3"],
  "file_type": "py"
}
```

To modify retrieval logic, edit `src/rag/retriever.py` and ensure it returns a list of dictionaries.

### Static Checker

To add a new check, create class in `src/checks/` and ensure it returns `Finding("check_name", "explanation_for_llm")`. If no issue, ensure the check returns `None`. Register checker classes in `src/checks/static_checker.py` and add it to `self.rules`.

### Prompts

To edit the prompt, go to `src/rag/prompt_builder.py` and edit the main function `build_prompt`.

## Notes

- Ensure Ollama is running before experimentation
- Ensure MongoDB connection is valid
- Large models require significant RAM
- RAG requires proper indexing to work

## License
This project is licensed under the MIT License – see the LICENSE file for details.