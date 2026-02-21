from google.adk.agents import LlmAgent
for key, value in LlmAgent.model_fields.items():
    print(f"{key}: {value.annotation}")
