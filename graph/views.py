from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from .models import Graph, Infection

import json
import networkx as nx
from networkx.readwrite import json_graph

######################################################################
# Index
def index(request, auto=True, data=None):
    #request.session.flush()
    
    # Define Current index
    current_index = request.session.get('current_index', 0)
    current_index_infection = request.session.get('current_index_infection', 0)

    if request.method == 'POST':
    	if request.POST.get('request') == 'new_graph':
    	    pass
        if request.POST.get('request') == 'existing_graph':
            current_index = int(request.POST.get('graph_id'))-1
            request.session.__setitem__('current_index', current_index)
        if request.POST.get('request') == 'infection':
            current_index_infection = int(request.POST.get('infection_id'))-1        
            request.session.__setitem__('current_index_infection', current_index_infection)
    
    # Latest graph/infection lists
    latest_graph_list = Graph.objects.order_by('id')
    latest_infection_list = Infection.objects.filter(graph=latest_graph_list[current_index]).order_by('id')

    # Define Context
    context = {'latest_graph_list': latest_graph_list, 
    'latest_infection_list': latest_infection_list, 
    'nodes': None, 
    'links': None, 
    'infected_nodes': [],
    'current_index': current_index+1, 
    'current_index_infection': current_index_infection+1}
    
    if auto:
        #current_graph_data = None
        #current_infection_graph_data = None
        current_graph_data = latest_graph_list[current_index].data
        if latest_infection_list:
            current_infection_graph_data = latest_infection_list[current_index_infection].data
            context['infected_nodes'] = json.dumps(current_infection_graph_data["nodes"])
    else:
        current_graph_data = data
        
    context['nodes'] = json.dumps(current_graph_data["nodes"])
    context['links'] = json.dumps(current_graph_data["links"])  
    
    request.session.__setitem__('data', current_graph_data)
    
    return render(request, 'graph/index.html', context)

######################################################################
def generate(request):
    if request.method == 'POST':
        generate_method_id = request.POST.get('generate_method')
        # FIXME : check if it is a number
        # TODO limit n
        n = int(request.POST.get('generate_n'))
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
        return index(request, auto=False, data=data)
    else:
        raise Http404('Error in generation')
    

def export_graph(request):
    data = request.session.get('data')
    s = json.dumps(data)
    
    response = HttpResponse(s, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="graph.json"'
    return response
    
def export_infection(request):
    pass

def detail(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    return render(request, 'graph/detail.html', {'graph': graph})
    
def select(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    return HttpResponseRedirect(reverse('graph:result', args=(graph.id,)))
    
def result(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    return render(request, 'graph/result.html', {'graph': graph})
