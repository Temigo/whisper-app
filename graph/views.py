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
        generate_method_id = request.query_params["generateMethod"]
        n = int(request.query_params["n"])

        generate_methods = {
        '1': nx.complete_graph,
        '2': nx.cycle_graph,
        '3': nx.circular_ladder_graph,
        '4': nx.dorogovtsev_goltsev_mendes_graph,
        '5': nx.empty_graph,
        '6': nx.hypercube_graph,
        '7': nx.ladder_graph,
        '8': nx.path_graph,
        '9': nx.star_graph,
        '10': nx.wheel_graph
        }

        try:
            generate_method = generate_methods[generate_method_id]
        except KeyError:
            raise Http404('Generation method doesn\'t exist.')

        g = generate_method(n)
        data = json_graph.node_link_data(g)
        return Response(data)

class Algorithm(APIView):
    def get(self, request, format=None):
        print(request.query_params)
        algorithm_id = request.query_params["algorithmMethod"]
        current_graph = request.query_params["currentGraph"]
        current_infection = request.query_params["currentInfection"]
        current_graph = json_graph.node_link_graph(json.loads(current_graph.encode('utf-8')))
        current_infection = json_graph.node_link_graph(json.loads(current_infection.encode('utf-8')))

        algorithm_methods = {
        '1': AlgorithmSZ,
        '2': AlgorithmNetsleuth,
        '3': AlgorithmPinto,
        '4': AlgorithmFC
        }
        algo = algorithm_methods[algorithm_id]()

        source = -1 # Default
        start_time = timeit.default_timer()
        if algorithm_id == '1':
            source = algo.run(current_graph, current_infection, v=int(request.query_params["v"]))
        if algorithm_id == '2':
            source = algo.run(current_graph, current_infection)[0]
        #if algorithm_id == '3':
        #    source = algo.run(current_graph, request.query_params["observers"], request.query_params["mean"], request.query_params["variance"])
        #if algorithm_id == '4':
        #    source = algo.run(current_graph, current_infection)[0]
        time_elapsed = timeit.default_timer() - start_time

        return Response({'source': source, 'timeElapsed': time_elapsed})

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

######################################################################
def import_infection(request):
    if request.method == 'POST':
        f = request.FILES['import_infection']
        # f.name
        if f.content_type == 'application/json':
            #with open('import_graph.json', 'wb+') as destination:
                #for chunk in f.chunks():
                #    destination.write(chunk)
                #
                #destination.close()
            data = json.load(f)
            return index(request, auto=False, data_infection=data)

        else:
            return index(request)
    else:
        return index(request)
