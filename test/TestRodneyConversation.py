from rodney_conversation.RodneyCommunication import RodneyCommunication

DIRECTIVE = ("Your directive is to assess the general level of satisfaction with the Texas A&M Engineering department, "
             "and see if there's anything that people complain about.")

if __name__ == "__main__":
    comms = RodneyCommunication(DIRECTIVE)
    comms.voice_conversation(verbose=True)
