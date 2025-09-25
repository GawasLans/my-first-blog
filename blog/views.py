from django.shortcuts import render, redirect, get_object_or_404
from .models import Practicante, Disciplina
from django.contrib import messages
from django.core.files.storage import FileSystemStorage


def index(request):
    """
    Esta vista maneja la página de inicio.
    """
    return render(request, 'blog/index.html')


def equipo(request):
    """
    Esta vista maneja la página del equipo y la lista de practicantes.
    """
    # Obtiene los practicantes de la base de datos, filtrados por disciplina y rol.
    practicantes_itf = Practicante.objects.filter(
        disciplina__nombre='Taekwon-Do ITF'
    ).order_by('apellido')
    
    practicantes_kombat = Practicante.objects.filter(
        disciplina__nombre='Kombat Taekwondo'
    ).order_by('apellido')
    
    profesores = Practicante.objects.filter(
        rol='profesor'
    ).order_by('apellido')
    
    # Obtiene todas las disciplinas para el formulario
    disciplinas = Disciplina.objects.all()

    # Crea el contexto para la plantilla
    contexto = {
        'practicantes_itf': practicantes_itf,
        'practicantes_kombat': practicantes_kombat,
        'profesores': profesores,
        'disciplinas': disciplinas,
    }
    
    return render(request, 'blog/equipo.html', contexto)


def crear_practicante(request):
    """
    Esta vista maneja la creación de un nuevo practicante.
    """
    if request.method == 'POST':
        # Aquí procesamos la información del formulario
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
        
        # Validar si el DNI ya existe
        if Practicante.objects.filter(dni=dni).exists():
            messages.error(request, 'Ya existe un practicante con este DNI.')
            return redirect('equipo')
        
        # Buscar la disciplina seleccionada
        try:
            disciplina = Disciplina.objects.get(pk=disciplina_id)
        except Disciplina.DoesNotExist:
            messages.error(request, 'La disciplina seleccionada no es válida.')
            return redirect('equipo')
            
        # Crear y guardar el nuevo practicante en la base de datos
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
        )
        
        # Guardar la imagen si existe
        if 'foto' in request.FILES:
            practicante.foto = request.FILES['foto']
            practicante.save()

        messages.success(request, '¡Practicante agregado exitosamente!')
        return redirect('equipo')
    
    # Manejar la solicitud GET para mostrar el formulario
    return redirect('equipo')

def detalle_practicante(request, practicante_id):
    """
    Esta vista muestra los detalles de un solo practicante.
    """
    practicante = get_object_or_404(Practicante, pk=practicante_id)
    return render(request, 'blog/detalle-practicante.html', {'practicante': practicante})

def editar_practicante(request, practicante_id):
    practicante = get_object_or_404(Practicante, pk=practicante_id)
    disciplinas = Disciplina.objects.all()

    if request.method == 'POST':
        # Validar si el DNI ya existe en otro practicante
        if Practicante.objects.filter(dni=request.POST.get('dni')).exclude(pk=practicante_id).exists():
            messages.error(request, 'Ya existe un practicante con este DNI.')
            return redirect('equipo')

        # Actualizar los campos del practicante
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
        
        # Manejar la foto, si se sube una nueva
        if 'foto' in request.FILES:
            practicante.foto = request.FILES['foto']
        
        practicante.save()
        messages.success(request, 'Practicante actualizado exitosamente.')
        return redirect('equipo')
    else:
        # Petición GET: Carga el formulario con los datos del practicante
        contexto = {
            'practicante': practicante,
            'disciplinas': disciplinas,
        }
        return render(request, 'blog/crear_practicante.html', contexto)

def eliminar_practicante(request, practicante_id):
    practicante = get_object_or_404(Practicante, pk=practicante_id)
    
    # Elimina la foto asociada al practicante antes de eliminar el objeto
    if practicante.foto:
        practicante.foto.delete()
        
    practicante.delete()
    messages.success(request, 'Practicante eliminado exitosamente.')
    return redirect('equipo')
