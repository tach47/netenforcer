#!/usr/bin/env python3

def yes_no(question):
    while True:
        answer = input("%s\n" % question)
        if (answer.lower() == 'yes' or answer.lower() == 'y'):
            return True
        elif (answer.lower() == 'no' or answer.lower() == 'n'):
            return False
        else:
            print("Only 'yes' or 'no' accepted.")
            continue


def question_answer(question):
    answer = input("%s\n" % question)
    return answer