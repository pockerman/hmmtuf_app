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

            state_names = []
            state1_name = request.POST.get('State[1][st_name]', "")

            if state1_name == "":
                template = loader.get_template(self._template_html)
                self._context.update({"error_missing_name": "State 1  name  not given"})
                self._response = HttpResponse(template.render(self._context, request))
                return not OK

            state_names.append(state1_name)
            state2_name = request.POST.get('State[2][st_name]', "")

            if state2_name == "":
                template = loader.get_template(self._template_html)
                self._context.update({"error_missing_name": "State 2  name  not given"})
                self._response = HttpResponse(template.render(self._context, request))
                return not OK
            elif state2_name in state_names:
                template = loader.get_template(self._template_html)
                self._context.update({"error_state_name_exists": "State 2 name {0} "
                                                                 "already exists".format(state2_name)})
                self._response = HttpResponse(template.render(self._context, request))
                return not OK

            # we need at least two states
            state_names.append(state2_name)

            counter = 3
            staten_name = 'State[{0}][st_name]'.format(counter)

            while staten_name in request.POST:
                state_name = request.POST.get(staten_name, "")

                if state_name == "":
                    template = loader.get_template(self._template_html)
                    self._context.update({"error_missing_name": "State {0}  name  not given".format(counter)})
                    self._response = HttpResponse(template.render(self._context, request))
                    return not OK
                elif state_name in state_names:
                    template = loader.get_template(self._template_html)
                    self._context.update(
                        {"error_state_name_exists": "State name {0} already exists".format(state_name)})
                    self._response = HttpResponse(template.render(self._context, request))
                    return not OK

                state_names.append(state_name)
                counter += 1
                staten_name = 'State[{0}][st_name]'.format(counter)

            self._states = {}

            for name in state_names:

                if name in self._states:
                    template = loader.get_template(self._template_html)
                    self._context.update({"error_name_exist": "State name {0} already exists".format(name)})
                    self._response = HttpResponse(template.render(self._context, request))
                    return not OK
                else:
                    self._states[name] = {}

            init_p_vector = request.POST.get('IPV-Value',  "")

            if init_p_vector == "":

                template = loader.get_template(self._template_html)
                self._context.update({"error_init_p_vector": "Initial probability vector not specified"})
                self._response = HttpResponse(template.render(self._context, request))
                return not OK

            init_p_vector = init_p_vector.split(',')
            if len(init_p_vector) != len(state_names):
                template = loader.get_template(self._template_html)
                self._context.update({"error_init_p_vector": "Initial probability vector "
                                                             "size not equal to number of states"})
                self._response = HttpResponse(template.render(self._context, request))
                return not OK

            for idx in range(len(init_p_vector)):
                init_p_vector[idx] = float(init_p_vector[idx])

            #print(init_p_vector)
            #print(len(init_p_vector))

            self._init_p_vector = dict()
            for name, prob in zip(self._states.keys(), init_p_vector):
                self._init_p_vector[name] = prob

            print(self._init_p_vector)

            for idx in range(len(self._states)):
                name = "State[{0}]".format(idx + 1)
                result = self._build_state(idx=idx, state_name=name,
                                           state_names=state_names, request=request)

                if result is not OK:
                    return result


            """
            self._states["State1"] = {"com_type": "SingleComponent",
                                      "distribution": "Normal",
                                      "parameters": {"means":[0.5, 0.3],
                                                     "vars": [0.5, 0.6]}}

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
            """

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

    def _build_state(self, idx, state_name, state_names, request):

        state_comp_type_key = state_name + "[com_type]"
        state_comp_type = request.POST.get(state_comp_type_key, "")

        if state_comp_type == "":
            template = loader.get_template(self._template_html)
            self._context.update({"error_state_comp": "State {0} "
                                                      "component not specified".format(state_names[idx])})
            self._response = HttpResponse(template.render(self._context, request))
            return not OK

        # set the component type either SingleComponent
        # or MixtureComponent
        self._states[state_names[idx]]["com_type"] = state_comp_type

        if state_comp_type == "SingleComponent":
            state_dist_type_key = state_name + "[distribution]"
            dist = request.POST.get(state_dist_type_key, "")

            if dist == "":
                template = loader.get_template(self._template_html)
                self._context.update({"error_dist_comp": "State {0} "
                                                         "distribution not specified".format(state_names[idx])})
                self._response = HttpResponse(template.render(self._context, request))
                return not OK

            self._states[state_names[idx]]["distribution"] = dist

            if dist == 'Normal':

                mu1_comp_key = state_name + "[single_com_m1]"
                mu1 = request.POST.get(mu1_comp_key, "")
                mu2_comp_key = state_name + "[single_com_m2]"
                mu2 = request.POST.get(mu2_comp_key, "")

                var1_comp_key = state_name + "[single_com_v1]"
                var2_comp_key = state_name + "[single_com_v2]"

                var1 = request.POST.get(var1_comp_key, "")
                var2 = request.POST.get(var2_comp_key, "")

                self._states[state_names[idx]]["parameters"] = {"means": [mu1, mu2], "vars": [var1, var2]}
                return OK
            elif dist == 'Uniform':

                comp_key_up_1 = state_name + "[single_com_u1]"
                up1 = request.POST.get(comp_key_up_1, "")

                comp_key_up_2 = state_name + "[single_com_u2]"
                up2 = request.POST.get(comp_key_up_2, "")

                comp_key_low_1 = state_name + "[single_com_l1]"
                low1 = request.POST.get(comp_key_low_1, "")

                comp_key_low_2 = state_name + "[single_com_l2]"
                low2 = request.POST.get(comp_key_low_2, "")

                self._states[state_names[idx]]["parameters"] = {"upper": [up1, up2], "lower": [low1, low2]}
                return OK
            else:

                template = loader.get_template(self._template_html)
                self._context.update({"error_dist_comp": "State {0} "
                                                         "distribution {1} does not exist".format(state_names[idx],
                                                                                                   dist)})
                self._response = HttpResponse(template.render(self._context, request))
                return not OK
        elif state_comp_type == "MixtureComponent":

            component_idx = 0
            dist_comp_key = state_name + "components[{0}][distribution]".format(component_idx)

            # try to find the components
            components = []
            while dist_comp_key in request.POST:

                dist = request.POST.get(dist_comp_key, "")

                if dist == "":
                    template = loader.get_template(self._template_html)
                    self._context.update({"error_dist_comp": "State {0} "
                                                             "distribution not specified".format(state_names[idx])})
                    self._response = HttpResponse(template.render(self._context, request))
                    return not OK

                if dist == 'Normal':

                    mu1_comp_key = state_name + "[single_com_m1]"
                    mu1 = request.POST.get(mu1_comp_key, "")
                    mu2_comp_key = state_name + "[single_com_m2]"
                    mu2 = request.POST.get(mu2_comp_key, "")

                    var1_comp_key = state_name + "[single_com_v1]"
                    var2_comp_key = state_name + "[single_com_v2]"

                    var1 = request.POST.get(var1_comp_key, "")
                    var2 = request.POST.get(var2_comp_key, "")

                    components.append({"distribution": "Normal", "parameters": {"means": [mu1, mu2], "vars": [var1, var2]}})

                    component_idx += 1
                    dist_comp_key = state_name + "components[{0}][distribution]".format(component_idx)

                elif dist == 'Uniform':

                    comp_key_up_1 = state_name + "[single_com_u1]"
                    up1 = request.POST.get(comp_key_up_1, "")

                    comp_key_up_2 = state_name + "[single_com_u2]"
                    up2 = request.POST.get(comp_key_up_2, "")

                    comp_key_low_1 = state_name + "[single_com_l1]"
                    low1 = request.POST.get(comp_key_low_1, "")

                    comp_key_low_2 = state_name + "[single_com_l2]"
                    low2 = request.POST.get(comp_key_low_2, "")

                    components.append({"distribution": "Uniform", "parameters": {"upper": [up1, up2], "lower": [low1, low2]}})

                    component_idx += 1
                    dist_comp_key = state_name + "components[{0}][distribution]".format(component_idx)
                else:

                    template = loader.get_template(self._template_html)
                    self._context.update({"error_dist_comp": "State {0} "
                                                             "distribution {1} does not exist".format(state_names[0], dist)})
                    self._response = HttpResponse(template.render(self._context, request))
                    return not OK

            self._states[state_names[idx]]["components"] = components
            return OK

