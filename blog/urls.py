# teamheroes/blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('equipo/', views.equipo, name='equipo'),
    path('practicante/crear/', views.crear_practicante, name='crear_practicante'),
    path('practicante/<int:practicante_id>/', views.detalle_practicante, name='detalle_practicante'),
    path('editar_practicante/<int:practicante_id>/', views.editar_practicante, name='editar_practicante'),
     path('eliminar_practicante/<int:practicante_id>/', views.eliminar_practicante, name='eliminar_practicante'),
]
