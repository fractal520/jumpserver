from django.urls import path

from .. import views

app_name = 'dreport'

urlpatterns = [
    path('CityView/', views.CityView.as_view(), name='CityView'),
    path('CityMonthView/', views.CityMonthView.as_view(), name='CityMonthView'),
    path('CityRecord/', views.CityRecord.as_view(), name='CityRecord'),
]
