from django.db import models

class Empresa(models.Model):
    # Identidad básica
    razon_social = models.CharField(max_length=100)
    nombre_comercial = models.CharField(max_length=100)
    ruc = models.CharField(max_length=13, unique=True)
    direccion = models.TextField(help_text="Av. 5 de octubre")
    telefono = models.CharField(max_length=15, null=True, blank=True)
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)
    correo = models.EmailField(unique=True)
    password_correo = models.CharField(max_length=255, blank=True, null=True)

    # Campos para la facturación electrónica (SRI)
    archivo_p12 = models.FileField(upload_to="firmas/", null=True, blank=True)
    # Usamos CharField para la clave, pero recuerda encriptarla antes de guardar
    password_p12_encriptada = models.CharField(max_length=255, null=True, blank=True)
    
    # El ambiente: 1 es Pruebas, 2 es Producción
    AMBIENTES = (
        ('1', 'Pruebas'),
        ('2', 'Producción'),
    )
    ambiente_sri = models.CharField(max_length=1, choices=AMBIENTES, default='1')
    
    # El secuencial debe ser de 9 dígitos. Empezamos en 1.
    contador_secuencial = models.PositiveIntegerField(default=1)

    # Datos del establecimiento (Obligatorios para el XML)
    cod_establecimiento = models.CharField(max_length=3, default='001', help_text="Ej: 001")
    cod_punto_emision = models.CharField(max_length=3, default='001', help_text="Ej: 001")

    # SaaS Control 
    activo = models.BooleanField(default=True)
    fecha_vencimiento_plan = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_comercial} RUC: ({self.ruc})"