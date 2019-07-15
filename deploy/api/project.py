# encoding: utf-8

from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response

from deploy.models import Project
from deploy.serializers import ProjectListSerializer, ProjectCreateSerializer
from common.permissions import IsValidUser
from common.utils import get_logger

logger = get_logger("jumpserver")


class ProjectListView(ListAPIView):

    queryset = Project.objects.all()
    permission_classes = (IsValidUser, )
    serializer_class = ProjectListSerializer


class ProjectCreateView(CreateAPIView):
    queryset = Project.objects.all()
    permission_classes = (IsValidUser, )
    serializer_class = ProjectCreateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        return super(ProjectCreateView, self).perform_create(serializer)


class ProjectDestroyView(DestroyAPIView):

    queryset = Project.objects.all()
    permission_classes = (IsValidUser, )
    serializer_class = ProjectListSerializer


class ProjectUpdateView(RetrieveUpdateAPIView):

    queryset = Project.objects.all()
    permission_classes = (IsValidUser,)
    serializer_class = ProjectListSerializer
