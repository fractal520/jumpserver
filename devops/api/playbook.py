# encoding: utf-8
import os

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from devops.serializers import TaskReadSerializer, TaskSerializer, AnsibleRoleSerializer
from devops.models import AnsibleRole, PlayBookTask
from devops.tasks import run_ansible_playbook, reset_task_playbook_path
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
        reset_task_playbook_path(task.id)
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


class TaskResetPlayBook(RetrieveAPIView):
    queryset = PlayBookTask.objects.all()
    serializer_class = TaskViewSet
    permission_classes = (IsOrgAdminOrAppUser,)

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        if reset_task_playbook_path(task.id):
            return Response(dict(code=200, msg=""))
        else:
            return Response(dict(code=400, error="Nothing"))


class InstallZipRoleView(CreateAPIView):
    """
        ansible-galaxy 安装 role
    """
    queryset = AnsibleRole.objects.all()
    serializer_class = AnsibleRoleSerializer
    permission_classes = (IsOrgAdminOrAppUser,)

    def create(self, request, *args, **kwargs):
        file = request.FILES['file_data']
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        #: 保存
        path = default_storage.save(os.path.join(settings.MEDIA_ROOT, 'tmp', '{}.zip'.format(file.name)),
                                    ContentFile(file.read()))
        #: 解压
        import zipfile
        f = zipfile.ZipFile(path, 'r')
        for file in f.namelist():
            f.extract(file, os.path.join(settings.PROJECT_DIR, 'data', 'playbooks', 'roles'))

        #: 删除
        default_storage.delete(path)

        #: 保存实例
        if not self.get_queryset().filter(name=request.data['name']).exists():
            serializer.save()
        headers = self.get_success_headers(serializer.data)
        #: 返回
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
