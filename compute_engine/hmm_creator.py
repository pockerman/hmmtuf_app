from pomegranate import *


def create_hmm_model_from_form(form):


    hmm_model = HiddenMarkovModel(name=form.hmm_name,
                                  start=None, end=None)

    form_states = form.states

    states = []
    for state in form_states:

        dist = state['distribution']
        states.append(dist, name=state['name'])

    # add states
    hmm_model.add_states(states)

    # setup initial probability
    init_p_vector = form.init_p_vector
    for idx in range(len(states)):
        hmm_model.add_transition(hmm_model.start, states[idx], init_p_vector[idx])


    # setup transition probabilities
    transition_probs = form.transition_probabilities

    for state1 in states:
        for state2 in states:
            hmm_model.add_transition(state1, state2, transition_probs[(state1.name, state2.name)])

    hmm_model.bake(verbose=True)
    return hmm_model

