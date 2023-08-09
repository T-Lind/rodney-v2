from rodney_ai.RodneyAi import RodneyAi

if __name__ == "__main__":
    ai = RodneyAi(
        "Your directive is to assess the general level of satisfaction with the Texas A&M Engineering department, and see if there's anything that people complain about.",
        verbose=True)

    print(ai.select_next_location())
