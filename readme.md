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



## License
This project is licensed under the MIT License – see the LICENSE file for details.