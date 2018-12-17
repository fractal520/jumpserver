# !/usr/bin/env python
# encoding: utf-8

from django.core.management.base import BaseCommand


class DemoCommand(BaseCommand):
    def handle(self, *args, **options):
        print("hello world!")
