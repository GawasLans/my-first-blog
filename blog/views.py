from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Practicante, Disciplina
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout

# Si usas el modelo Grado en tu proyecto, asegúrate de importarlo aquí:
# from .models import Practicante, Disciplina, Profesor, Kombat, ITF, Grado

# Credenciales únicas para el maestro
MASTER_USERNAME = "Gym"
MASTER_PASSWORD = "Heroes"

# --- VISTAS PRINCIPALES DE ACCESO Y AUTENTICACIÓN ---

def login_view(request):
    """
    Vista para manejar la entrada al sitio. Si se toca el botón 'Invitado', 
    redirige a la vista principal de invitado. Si es login, establece la sesión maestra.
    """
    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. Lógica de Entrada como Invitado (Redirige a la nueva ruta de inicio de invitado)
        if action == 'guest':
            # No se establece ninguna sesión de maestro
            return redirect('inicio_invitado')

        # 2. Lógica de Login Maestro
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == MASTER_USERNAME and password == MASTER_PASSWORD:
            # Establece la sesión maestra
            request.session['is_master'] = True
            messages.success(request, '¡Bienvenido maestro! Has iniciado sesión correctamente.')
            return redirect('index_maestro') # Redirige a la vista de maestro
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    
    # Muestra la página de login si es GET o si el POST falló
    return render(request, 'blog/login.html')

def logout_view(request):
    """
    Vista para cerrar la sesión del usuario maestro.
    """
    request.session.flush()
    messages.success(request, 'Has cerrado la sesión correctamente.')
    return redirect('login')


# --- VISTAS PARA EL MODO MAESTRO (CON PERMISOS DE EDICIÓN) ---

def index_maestro(request):
    """
    Página de inicio para el Maestro (acceso restringido/logueado).
    Usa la plantilla index.html
    """
    # Si no es maestro (o no está en sesión), redirige al login
    if not request.session.get('is_master'):
        return redirect('login') 
        
    try:
        # Obtener los objetos de disciplina para ITF y Kombat
        disciplina_itf = Disciplina.objects.get(nombre="Taekwon-Do ITF")
        disciplina_kombat = Disciplina.objects.get(nombre="Kombat Taekwondo")
        
        # Contar los practicantes para cada disciplina
        itf_count = Practicante.objects.filter(disciplina=disciplina_itf, rol='practicante').count()
        kombat_count = Practicante.objects.filter(disciplina=disciplina_kombat, rol='practicante').count()
        
    except Disciplina.DoesNotExist:
        itf_count = 0
        kombat_count = 0

    context = {
        'itf_count': itf_count,
        'kombat_count': kombat_count,
        'is_master': True # Siempre True en esta vista
    }
    return render(request, 'blog/index.html', context)


def equipo(request):
    """
    Renderiza la página del equipo para el MAESTRO (permite acciones).
    Usa la plantilla equipo.html
    """
    if not request.session.get('is_master'):
        return redirect('login')
        
    todos_los_practicantes = Practicante.objects.all()
    
    disciplina_itf = None
    disciplina_kombat = None
    try:
        disciplina_itf = Disciplina.objects.get(nombre="Taekwon-Do ITF")
        disciplina_kombat = Disciplina.objects.get(nombre="Kombat Taekwondo")
    except Disciplina.DoesNotExist:
        pass

    profesores = todos_los_practicantes.filter(rol='profesor')
    
    practicantes_itf = []
    if disciplina_itf:
        practicantes_itf = todos_los_practicantes.filter(disciplina=disciplina_itf, rol='practicante')
        
    practicantes_kombat = []
    if disciplina_kombat:
        practicantes_kombat = todos_los_practicantes.filter(disciplina=disciplina_kombat, rol='practicante')
    
    disciplinas = Disciplina.objects.all()

    context = {
        'practicantes_itf': practicantes_itf,
        'practicantes_kombat': practicantes_kombat,
        'profesores': profesores,
        'disciplinas': disciplinas,
        'itf_id': disciplina_itf.id if disciplina_itf else None,
        'kombat_id': disciplina_kombat.id if disciplina_kombat else None,
        'is_master': True
    }
    
    return render(request, 'blog/equipo.html', context)


def crear_practicante(request):
    """ Permite crear un practicante. Solo accesible si es maestro. """
    if not request.session.get('is_master'):
        messages.error(request, 'Acceso denegado. Solo el Maestro puede crear practicantes.')
        return redirect('index_maestro')

    # Obtener las opciones de días y horas del modelo Practicante
    try:
        dias_choices = Practicante.DIAS_CHOICES
        hora_choices = Practicante.HORA_CHOICES
    except AttributeError:
        dias_choices = []
        hora_choices = []


    if request.method == 'POST':
        # --- Lógica de Creación/Guardado ---
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        dni = request.POST.get('dni')
        genero = request.POST.get('genero')
        fecha_nacimiento = request.POST.get('fecha-nacimiento')
        pais = request.POST.get('pais')
        email = request.POST.get('email')
        peso = request.POST.get('peso') or None
        altura = request.POST.get('altura') or None
        disciplina_id = request.POST.get('disciplina')
        grado = request.POST.get('grado')
        licencia = request.POST.get('licencia')
        fecha_caducidad = request.POST.get('fecha-caducidad') or None
        rol = request.POST.get('rol', 'practicante')
        dias_entrenamiento = request.POST.get('dias-entrenamiento')
        hora_entrenamiento = request.POST.get('hora-entrenamiento')

        if Practicante.objects.filter(dni=dni).exists():
            messages.error(request, 'Ya existe un practicante con este DNI.')
            # Recargar contexto para mantener datos del formulario en caso de error
            disciplinas = Disciplina.objects.all()
            try:
                itf_disciplina = Disciplina.objects.get(nombre="Taekwon-Do ITF")
                kombat_disciplina = Disciplina.objects.get(nombre="Kombat Taekwondo")
                itf_id = itf_disciplina.id
                kombat_id = kombat_disciplina.id
            except ObjectDoesNotExist:
                itf_id = None
                kombat_id = None

            context = {
                'practicante': request.POST,
                'disciplinas': disciplinas,
                'itf_id': itf_id,
                'kombat_id': kombat_id,
                'dias_choices': dias_choices,
                'hora_choices': hora_choices,
                'is_master': True
            }
            return render(request, 'blog/crear_practicante.html', context)

        try:
            disciplina = Disciplina.objects.get(pk=disciplina_id)
        except ObjectDoesNotExist:
            messages.error(request, 'La disciplina seleccionada no es válida.')
            return redirect('equipo_maestro')

        practicante = Practicante.objects.create(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            genero=genero,
            fecha_nacimiento=fecha_nacimiento,
            pais=pais,
            email=email,
            peso=peso,
            altura=altura,
            disciplina=disciplina,
            grado=grado,
            licencia=licencia,
            fecha_caducidad=fecha_caducidad,
            rol=rol,
            dias_entrenamiento=dias_entrenamiento,
            hora_entrenamiento=hora_entrenamiento,
        )

        if 'foto' in request.FILES:
            practicante.foto = request.FILES['foto']
            practicante.save()

        messages.success(request, '¡Practicante agregado exitosamente!')
        return redirect('equipo_maestro')
        # --- Fin Lógica de Creación/Guardado ---
    
    else:
        disciplinas = Disciplina.objects.all()
        try:
            itf_disciplina = Disciplina.objects.get(nombre="Taekwon-Do ITF")
            kombat_disciplina = Disciplina.objects.get(nombre="Kombat Taekwondo")
            itf_id = itf_disciplina.id
            kombat_id = kombat_disciplina.id
        except ObjectDoesNotExist:
            itf_id = None
            kombat_id = None
        
        contexto = {
            'disciplinas': disciplinas,
            'itf_id': itf_id,
            'kombat_id': kombat_id,
            'dias_choices': dias_choices,
            'hora_choices': hora_choices,
            'is_master': True
        }
        
        return render(request, 'blog/crear_practicante.html', contexto)


def editar_practicante(request, practicante_id):
    """ Permite editar un practicante. Solo accesible si es maestro. """
    if not request.session.get('is_master'):
        messages.error(request, 'Acceso denegado. Solo el Maestro puede editar practicantes.')
        return redirect('index_maestro')

    practicante = get_object_or_404(Practicante, pk=practicante_id)
    disciplinas = Disciplina.objects.all()
    
    try:
        dias_choices = Practicante.DIAS_CHOICES
        hora_choices = Practicante.HORA_CHOICES
    except AttributeError:
        dias_choices = []
        hora_choices = []

    if request.method == 'POST':
        # --- Lógica de Edición/Guardado ---
        if Practicante.objects.filter(dni=request.POST.get('dni')).exclude(pk=practicante_id).exists():
            messages.error(request, 'Ya existe un practicante con este DNI.')
            # Recargar contexto en caso de error de DNI
            try:
                itf_disciplina = Disciplina.objects.get(nombre="Taekwon-Do ITF")
                kombat_disciplina = Disciplina.objects.get(nombre="Kombat Taekwondo")
                contexto = {
                    'practicante': practicante,
                    'disciplinas': disciplinas,
                    'itf_id': itf_disciplina.id,
                    'kombat_id': kombat_disciplina.id,
                    'dias_choices': dias_choices,
                    'hora_choices': hora_choices,
                    'is_master': True
                }
            except ObjectDoesNotExist:
                contexto = {
                    'practicante': practicante,
                    'disciplinas': disciplinas,
                    'dias_choices': dias_choices,
                    'hora_choices': hora_choices,
                    'is_master': True
                }
            return render(request, 'blog/crear_practicante.html', contexto)

        practicante.nombre = request.POST.get('nombre')
        practicante.apellido = request.POST.get('apellido')
        practicante.dni = request.POST.get('dni')
        practicante.genero = request.POST.get('genero')
        practicante.fecha_nacimiento = request.POST.get('fecha-nacimiento')
        practicante.pais = request.POST.get('pais')
        practicante.email = request.POST.get('email')
        practicante.peso = request.POST.get('peso') or None
        practicante.altura = request.POST.get('altura') or None
        practicante.disciplina_id = request.POST.get('disciplina')
        practicante.grado = request.POST.get('grado')
        practicante.licencia = request.POST.get('licencia') or None
        practicante.fecha_caducidad = request.POST.get('fecha-caducidad') or None
        practicante.rol = request.POST.get('rol')
        
        practicante.dias_entrenamiento = request.POST.get('dias-entrenamiento')
        practicante.hora_entrenamiento = request.POST.get('hora-entrenamiento')
        
        if 'foto' in request.FILES:
            practicante.foto = request.FILES['foto']
        
        practicante.save()
        messages.success(request, 'Practicante actualizado exitosamente.')
        return redirect('equipo_maestro')
        # --- Fin Lógica de Edición/Guardado ---
    
    else:
        try:
            itf_disciplina = Disciplina.objects.get(nombre="Taekwon-Do ITF")
            kombat_disciplina = Disciplina.objects.get(nombre="Kombat Taekwondo")
            contexto = {
                'practicante': practicante,
                'disciplinas': disciplinas,
                'itf_id': itf_disciplina.id,
                'kombat_id': kombat_disciplina.id,
                'dias_choices': dias_choices,
                'hora_choices': hora_choices,
                'is_master': True
            }
        except ObjectDoesNotExist:
            contexto = {
                'practicante': practicante,
                'disciplinas': disciplinas,
                'dias_choices': dias_choices,
                'hora_choices': hora_choices,
                'is_master': True
            }
        
        return render(request, 'blog/crear_practicante.html', contexto)

def eliminar_practicante(request, practicante_id):
    """ Permite eliminar un practicante. Solo accesible si es maestro. """
    if not request.session.get('is_master'):
        messages.error(request, 'Acceso denegado. Solo el Maestro puede eliminar practicantes.')
        return redirect('index_maestro')

    practicante = get_object_or_404(Practicante, pk=practicante_id)
    
    if practicante.foto:
        try:
            practicante.foto.delete()
        except:
             pass
        
    practicante.delete()
    messages.success(request, 'Practicante eliminado exitosamente.')
    return redirect('equipo_maestro')


# --- VISTAS PARA EL MODO INVITADO (SOLO LECTURA) ---

def inicio_invitado(request):
    """
    Página de inicio para los invitados. Muestra el conteo de practicantes (total e ITF).
    Usa la plantilla inicioinvitado.html
    """
    try:
        # 1. Contar el total de practicantes (CONTEO TOTAL)
        conteo_practicantes = Practicante.objects.count()

        # 2. Obtener el objeto de disciplina 'Taekwon-Do ITF'
        disciplina_itf = Disciplina.objects.get(nombre="Taekwon-Do ITF")
        
        # 3. AÑADIDO: Contar solo los practicantes de ITF, filtrando por el objeto Disciplina
        # Además, filtramos por rol='practicante' para ser consistentes con index_maestro
        itf_count = Practicante.objects.filter(
            disciplina=disciplina_itf, 
            rol='practicante'
        ).count()

    except Disciplina.DoesNotExist:
        # Si la disciplina "Taekwon-Do ITF" no existe en la BD
        conteo_practicantes = Practicante.objects.count() # El total sigue siendo válido
        itf_count = 0
    
    except Exception as e:
        # Manejo de otros errores (p. ej., problemas de base de datos)
        print(f"Error al contar practicantes: {e}")
        conteo_practicantes = 0
        itf_count = 0 

    context = {
        'conteo': conteo_practicantes,
        'itf_count': itf_count, # Esta variable se usa en tu HTML
        'is_master': False 
    }
    
    return render(request, 'blog/inicioinvitado.html', context)


def equipo_invitado(request):
    """
    Renderiza la página del equipo para el INVITADO (solo lectura).
    Usa la plantilla equipoinvitado.html
    """
    todos_los_practicantes = Practicante.objects.all()
    
    disciplina_itf = None
    disciplina_kombat = None
    try:
        disciplina_itf = Disciplina.objects.get(nombre="Taekwon-Do ITF")
        disciplina_kombat = Disciplina.objects.get(nombre="Kombat Taekwondo")
    except Disciplina.DoesNotExist:
        pass

    profesores = todos_los_practicantes.filter(rol='profesor')
    practicantes_itf = []
    if disciplina_itf:
        practicantes_itf = todos_los_practicantes.filter(disciplina=disciplina_itf, rol='practicante')
        
    practicantes_kombat = []
    if disciplina_kombat:
        practicantes_kombat = todos_los_practicantes.filter(disciplina=disciplina_kombat, rol='practicante')
    
    # Nota: No necesitamos pasar 'disciplinas', 'itf_id' o 'kombat_id' a un invitado,
    # pero las incluiremos para mantener la estructura si las usas en la plantilla.
    disciplinas = Disciplina.objects.all()

    context = {
        'practicantes_itf': practicantes_itf,
        'practicantes_kombat': practicantes_kombat,
        'profesores': profesores,
        'disciplinas': disciplinas,
        'itf_id': disciplina_itf.id if disciplina_itf else None,
        'kombat_id': disciplina_kombat.id if disciplina_kombat else None,
        'is_master': False # Siempre False en esta vista
    }
    # Asegúrate de crear el archivo 'blog/equipoinvitado.html'
    return render(request, 'blog/equipoinvitado.html', context)


# --- VISTAS AUXILIARES ---

def detalle_practicante(request, practicante_id):
    """ Vista de detalle para MAESTRO. Usa detalle-practicante.html """
    practicante = get_object_or_404(Practicante, pk=practicante_id)
    return render(request, 'blog/detalle-practicante.html', {'practicante': practicante, 'is_master': request.session.get('is_master', False)})

def detalle_practicante_invitado(request, practicante_id):
    """ Vista de detalle para INVITADO. Usa detalle-practicanteinvitado.html """
    practicante = get_object_or_404(Practicante, pk=practicante_id)
    return render(request, 'blog/detalle-practicanteinvitado.html', {
        'practicante': practicante, 
        'is_master': False # Siempre false para el invitado
    })

def obtener_grados(request):
    """
    Función de AJAX para obtener grados.
    """
    disciplina_id = request.GET.get('disciplina_id')
    try:
        from .models import Grado # Intenta importar Grado localmente
        grados = Grado.objects.filter(disciplina__id=disciplina_id).values('id', 'nombre').order_by('nombre')
    except (NameError, ImportError, ObjectDoesNotExist):
        return JsonResponse([], safe=False) 
        
    return JsonResponse(list(grados), safe=False)
