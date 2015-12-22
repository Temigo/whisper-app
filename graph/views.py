from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .models import Graph, Infection

import json

######################################################################
# Index
def index(request):
    #request.session.flush()
    current_index = request.session.get('current_index', 0)
    current_index_infection = request.session.get('current_index_infection', 0)

    if request.method == 'POST':
        if request.POST.get('request') == 'graph':
            current_index = int(request.POST.get('graph_id'))-1
            request.session.__setitem__('current_index', current_index)
        if request.POST.get('request') == 'infection':
            current_index_infection = int(request.POST.get('infection_id'))-1        
            request.session.__setitem__('current_index_infection', current_index_infection)
    
    
    latest_graph_list = Graph.objects.order_by('id')
    #latest_infection_list = Infection.objects.order_by('name')
    latest_infection_list = Infection.objects.filter(graph=latest_graph_list[current_index]).order_by('id')
    #current_graph_data = json.dumps(latest_graph_list[0].data)

    context = {'latest_graph_list': latest_graph_list, 
    'latest_infection_list': latest_infection_list, 
    'nodes': None, 
    'links': None, 
    'infected_nodes': [],
    'current_index': current_index+1, 
    'current_index_infection': current_index_infection+1}
    
    current_graph_data = None
    current_infection_graph_data = None
    if latest_graph_list:
        current_graph_data = latest_graph_list[current_index].data
        context['nodes'] = json.dumps(current_graph_data["nodes"])
        context['links'] = json.dumps(current_graph_data["links"])
    if latest_infection_list:
        current_infection_graph_data = latest_infection_list[current_index_infection].data
        context['infected_nodes'] = json.dumps(current_infection_graph_data["nodes"])

    print(context)
    return render(request, 'graph/index.html', context)

######################################################################
def detail(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    return render(request, 'graph/detail.html', {'graph': graph})
    
def select(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    return HttpResponseRedirect(reverse('graph:result', args=(graph.id,)))
    
def result(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    return render(request, 'graph/result.html', {'graph': graph})
