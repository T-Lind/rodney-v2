from rodney_ai.RodneyAi import RodneyAi
import openai
openai.api_key = "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"

if __name__ == "__main__":
    ai = RodneyAi(
        "Your directive is to assess the general level of satisfaction with the Texas A&M Engineering department, and see if there's anything that people complain about.",
        verbose=True)

    print(ai.select_next_location())
