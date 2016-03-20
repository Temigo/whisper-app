from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse

import json
import timeit
import networkx as nx
from networkx.readwrite import json_graph

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import GraphSerializer, InfectionSerializer
from .models import Graph, Infection

from .lib.algorithm_shah_zaman import AlgorithmSZ
from .lib.algorithm_netsleuth import AlgorithmNetsleuth
from .lib.algorithm_pinto import AlgorithmPinto
from .lib.algorithm_fioriti_chinnici import AlgorithmFC
from .lib import randomInfection

class GraphViewSet(viewsets.ModelViewSet):
    """
    API end-point for graphs
    """
    queryset = Graph.objects.all()
    serializer_class = GraphSerializer

class InfectionViewSet(viewsets.ModelViewSet):
    """
    API end-point for graphs
    """
    queryset = Infection.objects.all()
    serializer_class = InfectionSerializer

class GenerateGraph(APIView):
    def get(self, request, format=None):
        generate_method = json.loads(request.query_params["generateMethod"].encode('utf-8'))

        generate_method_id = generate_method["id"]
        params = generate_method["params"]
        generate_params = ()
        for param in params:
            generate_params = generate_params + (param['value'],)

        generate_methods = {
        1: nx.complete_graph,
        2: nx.cycle_graph,
        3: nx.circular_ladder_graph,
        4: nx.dorogovtsev_goltsev_mendes_graph,
        5: nx.empty_graph,
        6: nx.hypercube_graph,
        7: nx.ladder_graph,
        8: nx.path_graph,
        9: nx.star_graph,
        10: nx.wheel_graph,
        11: nx.balanced_tree,
        12: nx.barbell_graph,
        13: nx.grid_2d_graph,
        14: nx.lollipop_graph,
        15: nx.margulis_gabber_galil_graph,
        16: nx.chordal_cycle_graph,
        17: nx.bull_graph,
        18: nx.chvatal_graph,
        19: nx.moebius_kantor_graph,
        20: nx.karate_club_graph,
        21: nx.davis_southern_women_graph,
        22: nx.florentine_families_graph,
        23: nx.caveman_graph,
        24: nx.fast_gnp_random_graph,
        25: nx.newman_watts_strogatz_graph,
        26: nx.barabasi_albert_graph
        }

        try:
            generate_method = generate_methods[generate_method_id]
        except KeyError:
            raise Http404('Generation method doesn\'t exist.')

        g = generate_method(*generate_params)
        # Because otherwise json dumps tuples as lists
        if generate_method_id in [6, 13]:
            g = nx.convert_node_labels_to_integers(g)

        data = json_graph.node_link_data(g)
        return Response(data)

class SimulateInfection(APIView):
    def get(self, request, format=None):
        print(request.query_params)
        current_graph = request.query_params["currentGraph"]
        current_graph = json_graph.node_link_graph(json.loads(current_graph.encode('utf-8')))
        seeds = json.loads(request.query_params["seeds"].encode('utf-8'))
        seeds = seeds["data"]
        ratio = float(request.query_params["ratio"])
        proba = float(request.query_params["proba"])

        infection = randomInfection.Infection()
        infection_graph = infection.run(current_graph, seeds, ratio, proba)

        print(json_graph.node_link_data(infection_graph))
        return Response({'infectionGraph': json_graph.node_link_data(infection_graph)})

class Algorithm(APIView):
    def get(self, request, format=None):
        print(request.query_params)
        algorithmMethod = json.loads(request.query_params["algorithmMethod"].encode('utf-8'))
        algorithm_id = algorithmMethod['id']
        current_graph = request.query_params["currentGraph"]
        current_infection = request.query_params["currentInfection"]
        current_graph = json_graph.node_link_graph(json.loads(current_graph.encode('utf-8')))
        current_infection = json_graph.node_link_graph(json.loads(current_infection.encode('utf-8')))
        times = int(request.query_params["times"])

        params = algorithmMethod["params"]
        algorithm_params = ()
        for param in params:
            if ('selectNodes' in param):
                algorithm_params = algorithm_params + (param['nodes'],)
            else:
                algorithm_params = algorithm_params + (param['value'],)

        print(algorithm_params)
        algorithm_methods = {
        1: AlgorithmSZ,
        2: AlgorithmNetsleuth,
        3: AlgorithmPinto,
        4: AlgorithmFC
        }
        algo = algorithm_methods[algorithm_id]()

        time_elapsed = []
        sources = []
        for i in range(times):
            start_time = timeit.default_timer()
            #if algorithm_id == '1':
            #    source = algo.run(current_graph, current_infection, v=int(request.query_params["v"]))
            #if algorithm_id == '2':
            #    source = algo.run(current_graph, current_infection)[0]
            sources.extend(algo.run(current_graph, current_infection, *algorithm_params))
            #if algorithm_id == '3':
            #    source = algo.run(current_graph, request.query_params["observers"], request.query_params["mean"], request.query_params["variance"])
            #if algorithm_id == '4':
            #    source = algo.run(current_graph, current_infection)[0]
            time_elapsed.append(timeit.default_timer() - start_time)

        if sources:
            return Response({'source': sources, 'timeElapsed': time_elapsed})
        else:
            return Response({'source': -1, 'timeElapsed': time_elapsed})

######################################################################
def import_algorithm(request):
    print("Hello")
    if request.method == 'POST':

        f = request.FILES['import_algorithm']
        # f.name
        print(f.content_type)
        if f.content_type == 'text/x-python':
            #with open('import_graph.json', 'wb+') as destination:
                #for chunk in f.chunks():
                #    destination.write(chunk)
                #
                #destination.close()
            print(f)

            return index(request, auto=True)

        else:
            print("Not good")
            return index(request)
    else:
        return index(request)
