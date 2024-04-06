from django import template

register = template.Library()


@register.inclusion_tag("correct_answer.html", takes_context=True)
def correct_answer_for_all(context, question):
    """
    processes the correct answer based on a given question object
    if the answer is incorrect, informs the user
    """
    if hasattr(question, "get_choices"):
        answers = question.get_choices()
        answer_format = "choices"
    else:
        # For descriptive questions, there may not be a 'get_choices' method
        answers = getattr(question, "sample_answer", "No specific answer required.")
        answer_format = "text"

    incorrect_list = context.get("incorrect_questions", [])

    if question.id in incorrect_list:
        user_was_incorrect = True
    else:
        user_was_incorrect = False

    return {
        "previous": {"answers": answers, "answer_format": answer_format},
        "user_was_incorrect": user_was_incorrect,
    }


@register.filter
def answer_choice_to_string(question, answer):

    if hasattr(question, "answer_choice_to_string"):
        try:
            return question.answer_choice_to_string(answer)
        except Exception as e:
            return "Choice not found."
    return str(answer)
