from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from devops.serializers import TaskReadSerializer, TaskSerializer, AnsibleRoleSerializer
from devops.models import AnsibleRole, PlayBookTask
from devops.tasks import run_ansible_playbook
from common.permissions import IsOrgAdminOrAppUser, IsValidUser


class PlayBookTaskListViewApi(ListAPIView):
    queryset = PlayBookTask.objects.all()
    permission_classes = (IsValidUser, )
    serializer_class = TaskReadSerializer


class TaskOperationViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """
        对Ansible的task提供的 操作 API操作
    """
    queryset = PlayBookTask.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsOrgAdminOrAppUser,)

    def update(self, request, *args, **kwargs):
        response = super(TaskOperationViewSet, self).update(request, *args, **kwargs)
        task = self.get_object()
        return response

    def create(self, request, *args, **kwargs):
        response = super(TaskOperationViewSet, self).create(request, *args, **kwargs)
        task = PlayBookTask.objects.get(id=response.data['id'])
        task.created_by = request.user.name
        task.save()
        return response


class AnsibleRoleViewSet(viewsets.ModelViewSet):
    """
        对AnsibleRole提供的API操作
    """
    queryset = AnsibleRole.objects.all()
    serializer_class = AnsibleRoleSerializer
    permission_classes = (IsOrgAdminOrAppUser,)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = PlayBookTask.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsOrgAdminOrAppUser,)
    label = None
    help_text = ''


class TaskRun(RetrieveAPIView):
    queryset = PlayBookTask.objects.all()
    serializer_class = TaskViewSet
    permission_classes = (IsOrgAdminOrAppUser,)

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        t = run_ansible_playbook(str(task.id))
        return Response(dict(code=200, msg=str(t)))
