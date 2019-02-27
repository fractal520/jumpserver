from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from common.utils import get_logger
from .pjenkins.exec_jenkins import JenkinsWork
from .models.deploy_list import DeployList, create_or_update, DeployVersion
from .forms.deployapp import AppUpdateForm
# Create your views here.

logger = get_logger('jumpserver')


class DeployIndex(LoginRequiredMixin, ListView):
    model = DeployList
    template_name = 'deploy/deploy_list.html'
    context_object_name = 'deploys'


def get_jenkins_all(request):
    jobs = JenkinsWork().collect_all_job()
    logger.info('开始获取Jenkins数据')
    create_or_update(jobs)
    return JsonResponse(dict(code=200))


def build_app(request):
    job_id = request.GET.get('id')
    try:
        job = DeployList.objects.get(id=job_id)
    except BaseException as error:
        logger.error(error)
        return JsonResponse(dict(code=400, error='error'))
    logger.info('发送构建{0}请求到Jenkins'.format(job.app_name))
    JenkinsWork().build_job(job.app_name)
    return JsonResponse(dict(code=200, mgs='success'))


class DeployOptionList(LoginRequiredMixin, DetailView):
    model = DeployList
    template_name = 'deploy/deploy_detail.html'
    context_object_name = 'result'
    object = None

    def get_context_data(self, **kwargs):
        context = {
            'app': _('deploy'),
            'action': _('Depoly detail')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class DeployUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = DeployList
    form_class = AppUpdateForm
    template_name = 'deploy/deploy_update.html'
    success_url = reverse_lazy('deploy:deploy_list')

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Deploy'),
            'action': _('Update Deploy'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class DeployRollbackView(LoginRequiredMixin, DetailView):
    model = DeployList
    template_name = 'deploy/deploy_rollback.html'
    context_object_name = 'result'
    object = None

    def get_context_data(self, **kwargs):
        context = {
            'app': _('deploy'),
            'action': _('Rollback'),
            'version': DeployVersion.objects.filter(app_name_id=self.object.id).order_by('-create_time')[:5]
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class AppStatusView(LoginRequiredMixin, DetailView):
    model = DeployList
    template_name = 'deploy/app_status.html'
    context_object_name = 'result'
    object = None

    def get_context_data(self, **kwargs):
        context = {
            'app': _('deploy'),
            'action': _('AppStatus'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
