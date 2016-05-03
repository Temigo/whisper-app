from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse

import json, csv
import timeit
import networkx as nx
from networkx.readwrite import json_graph
import logging
import coloredlogs
import numpy

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r
from .serializers import GraphSerializer, InfectionSerializer
from .models import Graph, Infection

from .lib.algorithm_shah_zaman import AlgorithmSZ
from .lib.algorithm_netsleuth import AlgorithmNetsleuth
from .lib.algorithm_pinto import AlgorithmPinto
from .lib.algorithm_fioriti_chinnici import AlgorithmFC
from .lib.algorithm_remi import AlgorithmRemi
from .lib import randomInfection, forceFrontier
from .lib.algorithm_remi_original import AlgorithmRemiOriginal
from .lib.algorithm_henri import AlgorithmHenri

from RestrictedPython import compile_restricted
from RestrictedPython.PrintCollector import PrintCollector
_print_ = PrintCollector
from RestrictedPython.Guards import full_write_guard
_write_ = full_write_guard
_getattr_ = getattr

#logging.basicConfig(level=logging.DEBUG)
# coloredlogs.install(level='DEBUG')
# logger = logging.getLogger(__name__)
#logger.propagate = False # Not enabled yet

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

class ImportGraph(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        file_obj = request.data['file']
        # logger.info("Post Graph")
        # logger.debug(file_obj)

        graph = None
        data = {}
        if file_obj.name.endswith('.paj') or file_obj.name.endswith('.net'):
            graph = nx.read_pajek(file_obj)
            graph.name = file_obj.name # FIXME
            data = json_graph.node_link_data(graph)
        elif file_obj.name.endswith('.json'):
            data = json.load(file_obj)


        #logger.debug(data)
        return Response(data)

class GenerateGraph(APIView):
    def post(self, request, format=None):
        # logger.info("Generate Graph")
        generate_method = request.data["generateMethod"]
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
            # logger.error('Generation method doesn\'t exist.')
            raise Http404('Generation method doesn\'t exist.')

        g = generate_method(*generate_params)
        # Because otherwise json dumps tuples as lists
        if generate_method_id in [6, 13]:
            g = nx.convert_node_labels_to_integers(g)

        positions = {}
        if g.number_of_nodes() <= 1000:
            positions = nx.spring_layout(g)

        data = {'graph': json_graph.node_link_data(g), 'positions': positions}
        return Response(data)

class SimulateInfection(APIView):
    def post(self, request, format=None):
        # logger.info("Simulate infection")
        # logger.debug(request.query_params)
        current_graph = request.data["currentGraph"]
        current_graph = json_graph.node_link_graph(current_graph)
        seeds = request.data["seeds"]
        seeds = seeds["data"]
        ratio = float(request.data["ratio"])
        proba = float(request.data["proba"])

        infection = randomInfection.Infection()
        infection_graph = infection.run(current_graph, seeds, ratio, proba)
        # logger.debug(json_graph.node_link_data(infection_graph))
        return Response({'infectionGraph': json_graph.node_link_data(infection_graph)})

class Algorithm(APIView):
    #renderer_classes = [r.CSVRenderer] + api_settings.DEFAULT_RENDERER_CLASSES
    #renderer_classes = (r.CSVRenderer,)

    def compute_measurement_2(self, current_graph, ratio, proba, algo, infection, algorithm_params, average_times, seed, new_seeds, datas=None):
        datas = datas if datas else []
        for i in range(min(average_times, 500)):
            infection_graph = infection.run(current_graph, new_seeds, ratio, proba)
            new_sources = algo.run(current_graph, infection_graph, *algorithm_params)
            for source in new_sources:
                datas.append(nx.astar_path_length(current_graph, source, seed))
                # FIXME distance source -> seed or source -> node
        return datas

    def post(self, request, format=None):
        # logger.info("Apply algorithm")
        # logger.debug(request.data)
        algorithmMethod = request.data["algorithmMethod"]
        algorithm_id = int(algorithmMethod['id'])
        current_graph = request.data["currentGraph"]
        current_infection = request.data["currentInfection"]
        current_graph = json_graph.node_link_graph(current_graph)
        current_infection = json_graph.node_link_graph(current_infection)
        times = int(request.data["times"])
        average_times = int(request.data["average"])
        detailed = request.data["detailed"]
        measure = request.data["measure"]
        seeds = request.data["seeds"]
        ratio = request.data["ratio"] if request.data["ratio"] != 0 else 0.5
        proba = request.data["proba"] if request.data["proba"] != 0 else 0.5

        params = algorithmMethod["params"]
        algorithm_params = ()
        for param in params:
            if ('selectNodes' in param):
                algorithm_params = algorithm_params + (param['nodes'],)
            else:
                algorithm_params = algorithm_params + (param['value'],)

        # logger.debug(algorithm_params)

        algorithm_methods = {
        1: AlgorithmSZ,
        2: AlgorithmNetsleuth,
        3: AlgorithmPinto,
        4: AlgorithmFC,
        5: AlgorithmRemiOriginal,
        6: AlgorithmRemi,
        7: AlgorithmHenri
        }

        if algorithm_id == -1: # Custom algorithm
            custom_algorithm = request.data["algo"]
            exec(custom_algorithm)
            # code = compile_restricted(custom_algorithm, '<string>', 'exec')
            # exec(code)
            algo = CustomAlgorithm()
        else:
            algo = algorithm_methods[algorithm_id]()

        error = ""
        try:
            infection = randomInfection.Infection()
            if not detailed:
                time_elapsed = []
                sources = []
                for i in range(times):
                    start_time = timeit.default_timer()
                    sources.extend(algo.run(current_graph, current_infection, *algorithm_params))
                    time_elapsed.append(timeit.default_timer() - start_time)

                # Measurement 1 : distance from source to seed
                distances = {}
                if measure:
                    for source in sources:
                        distances[source] = {}
                        for seed in seeds:
                            distances[source][seed] = nx.astar_path_length(current_graph, source, seed)

                # Measurement 2 : Stability
                datas = []
                if measure:
                    if algorithm_id != 3:
                        for seed in seeds:
                            for node in current_graph.neighbors(seed):
                                if node not in seeds:
                                    new_seeds = seeds[:]
                                    new_seeds.remove(seed)
                                    datas = self.compute_measurement_2(current_graph, ratio, proba, algo, infection, algorithm_params, average_times, node, new_seeds+[node], datas)
                datas = numpy.array(datas)

                return Response({'source': sources if sources else -1,
                                'timeElapsed': time_elapsed,
                                'distances': distances,
                                'diameter': nx.diameter(current_graph),
                                'mean': numpy.mean(datas) if datas.size else -1,
                                'variance': numpy.var(datas) if datas.size else -1,
                                'error': str(error)})
            else: # Detailed study
                detailed_datas = []
                diameter = nx.diameter(current_graph)
                for node in current_graph:
                    temp = {}
                    temp["node"] = node
                    temp["diameter"] = diameter
                    temp["degree"] = current_graph.degree(node)
                    infection_graph = infection.run(current_graph, [node], ratio, proba)
                    new_sources = algo.run(current_graph, infection_graph, *algorithm_params)
                    temp["sources"] = []
                    for source in new_sources:
                        temp2 = {}
                        temp2["source"] = source
                        temp2['distance'] = nx.astar_path_length(current_graph, node, source)
                        datas = numpy.array(self.compute_measurement_2(current_graph, ratio, proba, algo, infection, algorithm_params, average_times, node, [source]))
                        temp2["mean"] = numpy.mean(datas)
                        temp2["variance"] = numpy.var(datas)
                        temp["sources"].append(temp2)
                    detailed_datas.append(temp)
                # print detailed_datas
                return Response({"data": r.CSVRenderer().render(detailed_datas)})
                #return Response({"data": detailed_datas})

        except Exception as e:
            error = e
            raise e
            return Response({'source': sources if sources else -1,
                            'timeElapsed': time_elapsed,
                            'error': str(error)})


class Frontier(APIView):
    def post(self, request, format=None):
        # logger.debug(request.query_params)
        current_infection = request.data["currentInfection"]
        current_infection = json_graph.node_link_graph(current_infection)

        f = forceFrontier.ForceFrontier()
        return Response({'convexHull' : f.run(current_infection)})

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
