from django.urls import path

from .. import views

app_name = 'dreport'

urlpatterns = [
    path('CityView/', views.CityView.as_view(), name='CityView'),
    path('CityView/<uuid:pk>/update/', views.CityUpdateView.as_view(), name='city-update'),
    path('CityView/create/', views.CityCreateView.as_view(), name='city-create'),
    path('CityMonthView/', views.CityMonthView.as_view(), name='CityMonthView'),
    path('CityRecord/', views.CityRecord.as_view(), name='CityRecord'),
    path('CityRecord/<uuid:pk>/update/', views.RecordUpdateView.as_view(), name='record-update'),
]
