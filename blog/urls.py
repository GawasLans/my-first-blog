# teamheroes/blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ----------------------------------------------------------------------
    # 1. RUTAS DE ACCESO (Públicas)
    # ----------------------------------------------------------------------
    
    path('', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),

    # ----------------------------------------------------------------------
    # 2. RUTAS DE MAESTRO (Protegidas)
    # ----------------------------------------------------------------------
    
    path('maestro/inicio/', views.index_maestro, name='index_maestro'), 
    path('maestro/equipo/', views.equipo, name='equipo_maestro'), 
    
    # CRUD completo (solo para el maestro)
    path('maestro/practicante/crear/', views.crear_practicante, name='crear_practicante'),
    path('maestro/practicante/editar/<int:practicante_id>/', views.editar_practicante, name='editar_practicante'),
    path('maestro/practicante/eliminar/<int:practicante_id>/', views.eliminar_practicante, name='eliminar_practicante'),
    
    # Detalle de Maestro (usa detalle-practicante.html)
    path('maestro/practicante/detalle/<int:practicante_id>/', views.detalle_practicante, name='detalle_practicante_maestro'),
    
    # ----------------------------------------------------------------------
    # 3. RUTAS DE INVITADO (Solo Lectura)
    # ----------------------------------------------------------------------

    path('invitado/inicio/', views.inicio_invitado, name='inicio_invitado'),
    path('invitado/equipo/', views.equipo_invitado, name='equipo_invitado'),
    
    # Detalle de Invitado (usa detalle-practicanteinvitado.html)
    path('invitado/practicante/detalle/<int:practicante_id>/', views.detalle_practicante_invitado, name='detalle_practicante_invitado'), 

    # ----------------------------------------------------------------------
    # 4. RUTAS AUXILIARES (Públicas o compartidas)
    # ----------------------------------------------------------------------

    path('obtener-grados/', views.obtener_grados, name='obtener_grados'),
]
