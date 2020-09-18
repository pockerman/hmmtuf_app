from django.http import HttpResponse
from django.template import loader
from compute_engine.constants import OK
from hmmtuf import INVALID_ITEM
from hmmtuf_home.models import HMMModel

class HMMFormCreator(object):

    def __init__(self, template, context):
        self._template_html = template
        self._context = context
        self._response = INVALID_ITEM
        self._hmm_name = INVALID_ITEM
        self._init_p_vector = INVALID_ITEM
        self._states = INVALID_ITEM
        self._transition_probabilities = INVALID_ITEM

    @property
    def response(self):
        return self._response

    @property
    def hmm_name(self):
        return self._hmm_name

    @property
    def states(self):
        return self._states

    @property
    def transition_probabilities(self):
        return self._transition_probabilities

    @property
    def init_p_vector(self):
        return self._init_p_vector

    def check(self, request):

        #import pdb
        #pdb.set_trace()
        self._hmm_name = request.POST.get("hmm-name", "")

        print(request.POST)

        for name in request.POST:
            print(name)
            print(request.POST.get(name))

        if self._hmm_name == "":
            template = loader.get_template(self._template_html)
            self._context.update({"error_missing_name": "No HMM name specified"})
            self._response = HttpResponse(template.render(self._context, request))
            return not OK

        try:
            model = HMMModel.objects.get(name=self._hmm_name)
            template = loader.get_template(self._template_html)
            self._context.update({"error_name_exist": "HMM  with name {0} already exists".format(self._hmm_name)})
            self._response = HttpResponse(template.render(self._context, request))
            return not OK
        except:

            #import pdb
            #pdb.set_trace()

            self._states = {}
            state_names =[]
  
            
            for s in states:
                print("I m here")
                print (states[s])

            if state_names is None:
                template = loader.get_template(self._template_html)
                self._context.update({"error_no_states": "The HMM has no states specified"})
                self._response = HttpResponse(template.render(self._context, request))
                return not OK

            for name in state_names:

                if name in self._states:
                    template = loader.get_template(self._template_html)
                    self._context.update({"error_name_exist": "State name {0} already exists".format(name)})
                    self._response = HttpResponse(template.render(self._context, request))
                    return not OK
                else:
                    self._states[name]={}

            init_p_vector = request.POST.get('IPV-Value',  None)

            print(init_p_vector)
            print(len(init_p_vector))

            init_p_vector = [0.1, 0.8, 0.1]
            self._init_p_vector = dict()
            for name, prob in zip(self._states.keys(), init_p_vector):
                self._init_p_vector[name] = prob

            print(self._init_p_vector)

            self._states["State1"] = {"com_type": "SingleComponent",
                                      "distribution": "Normal",
                                      "parameters": {"means":[0.5, 0.3],"vars": [0.5, 0.6]}}

            self._states["State2"] = {"com_type": "SingleComponent",
                                      "distribution": "Uniform",
                                      "parameters": {"upper": [0.5, 0.3],
                                                     "lower": [0.5, 0.6]}}

            self._states["State3"] = {"com_type": "MixtureComponent",
                                      "components": [{"distribution": "Normal",
                                                      "parameters": {"means": [0.5, 0.3],
                                                                     "vars": [0.5, 0.6]}
                                                      },
                                                     {"distribution": "Normal",
                                                      "parameters": {"means": [0.5, 0.3],
                                                                     "vars": [0.5, 0.6]}
                                                      },
                                                     ],
                                      "weighs": [0.5, 0.5]
            }

            self._transition_probabilities = dict()
            self._transition_probabilities[("State1", "State1")] = 0.8
            self._transition_probabilities[("State2", "State2")] = 0.8
            self._transition_probabilities[("State3", "State3")] = 0.8
            self._transition_probabilities[("State1", "State2")] = 0.1
            self._transition_probabilities[("State1", "State3")] = 0.1
            self._transition_probabilities[("State2", "State1")] = 0.1
            self._transition_probabilities[("State2", "State3")] = 0.1
            self._transition_probabilities[("State3", "State1")] = 0.1
            self._transition_probabilities[("State3", "State2")] = 0.1
            return OK

    def as_map(self):
        return {"transition_probabilities": self._transition_probabilities,
                "states": self._states,
                "init_p_vector": self._init_p_vector,
                "hmm_name": self._hmm_name}

