# encoding: utf-8

import json
import requests as Requests

from django.conf import settings
from rest_framework.generics import RetrieveAPIView, CreateAPIView, GenericAPIView
from rest_framework.response import Response

from common.permissions import IsValidUser
from assets.models import Asset


class CheckFileListAPIView(RetrieveAPIView):

    queryset = None
    permission_classes = (IsValidUser,)

    def retrieve(self, request, *args, **kwargs):
        response = Requests.get(url="http://{}/api/list/run/jobs".format(settings.RDM_URL))
        data = response.json()
        data = data.get('data')
        data_list = []
        for key, value in data.items():
            value['job_id'] = key
            data_list.append(value)
        return Response(data_list)


class CreateFileCheckJobAPIView(CreateAPIView):

    queryset = None
    permission_classes = (IsValidUser,)

    def post(self, request, *args, **kwargs):
        code = 200
        msg = ""
        for key, value in request.data.items():
            if not value:
                code = 400
                msg += "\n{}不能为空".format(key)
        if code != 200:
            return Response(dict(code=code, msg=msg))
        else:
            data = {key: value for key, value in request.data.items()}
            data.pop('csrfmiddlewaretoken')
            asset = Asset.objects.get(id=data.get('asset_id'))
            data["node_ip"] = asset.ip
            response = Requests.post(url="http://{}/api/add/job/".format(settings.RDM_URL), json=json.dumps(data))
            msg = json.loads(response.text).get('msg')
            return Response(dict(code=response.status_code, msg=msg))


class DeleteFileCheckJobAPIView(GenericAPIView):

    queryset = None
    permission_classes = (IsValidUser,)

    def get(self, request, *args, **kwargs):
        job_id = kwargs.get('pk')
        the_url = "http://{}/api/delete/job/{}".format(settings.RDM_URL, job_id)
        response = Requests.get(url=the_url)
        code = response.status_code
        msg = json.loads(response.text).get('msg')
        return Response(dict(code=code, msg=msg))
