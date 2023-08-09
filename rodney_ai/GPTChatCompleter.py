from langchain.llms import OpenAI


def get_gpt_completions(prompt, max_tokens=100, model="gpt-4"):
    return OpenAI(model_name=model, max_tokens=max_tokens,
                  openai_api_key="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")(prompt)
