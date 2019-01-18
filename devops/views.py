from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from assets.models import Asset, AdminUser, SystemUser, Label, Node, Domain

# Create your views here.


def index(request):
    print('devops_index')
    return JsonResponse(dict(code=200, msg='devops index'))


class AssetListView(LoginRequiredMixin, TemplateView):
    template_name = 'devops/asset_list.html'

    def get_context_data(self, **kwargs):
        Node.root()
        context = {
            'app': _('Assets'),
            'action': _('Asset list'),
            'labels': Label.objects.all().order_by('name'),
            'nodes': Node.objects.all().order_by('-key'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
