from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

class Disciplina(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/')
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre



class Practicante(models.Model):
    GENERO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]

    ROL_CHOICES = [
        ('practicante', 'Practicante'),
        ('profesor', 'Profesor'),
    ]

    DIAS_CHOICES = [
        ('Lunes Miércoles y Viernes', 'Lunes, Miércoles y Viernes'),
        ('Miércoles/Viernes', 'Miércoles y Viernes'),
        ('Martes y Jueves', 'Martes y Jueves'),
    ]

    HORA_CHOICES = [
        ('14:30', '14:30'),
        ('15:30', '15:30'),
        ('17:45', '17:45'),
        ('18:30', '18:30'),
        ('19:30', '19:30'),
        ('20:30', '20:30'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES)
    fecha_nacimiento = models.DateField()
    pais = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)

    grado = models.CharField(max_length=50, null=True, blank=True)
    licencia = models.CharField(max_length=50, null=True, blank=True)
    fecha_caducidad = models.DateField(null=True, blank=True)

    foto = models.ImageField(upload_to='practicantes/', null=True, blank=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='practicante')

    # ✅ Solo una vez los campos de días y horas
    dias_entrenamiento = models.CharField(
        max_length=50,
        choices=DIAS_CHOICES,
        blank=True,
        null=True,
        verbose_name="Días de Entrenamiento"
    )
    hora_entrenamiento = models.CharField(
        max_length=5,
        choices=HORA_CHOICES,
        blank=True,
        null=True,
        verbose_name="Hora de Entrenamiento"
    )

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

