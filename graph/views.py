from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from .models import Graph

import json

def index(request):
    latest_graph_list = Graph.objects.order_by('name')[:5]
    #current_graph_data = json.dumps(latest_graph_list[0].data)
    current_index = 0
    if request.method == 'POST':
        current_index = int(request.POST['graph_id'])-1
        request.session.__setitem__('current_index', current_index)
    else:
        if request.session.__contains__('current_index'):
        	current_index = request.session.__getitem__('current_index')
    	
    current_graph_data = latest_graph_list[current_index].data
    context = {'latest_graph_list': latest_graph_list, 'nodes': json.dumps(current_graph_data["nodes"]), 'links': json.dumps(current_graph_data["links"]), 'current_index': current_index+1}
    return render(request, 'graph/index.html', context)

def detail(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    return render(request, 'graph/detail.html', {'graph': graph})
    
def select(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    return HttpResponseRedirect(reverse('graph:result', args=(graph.id,)))
    
def result(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    return render(request, 'graph/result.html', {'graph': graph})
