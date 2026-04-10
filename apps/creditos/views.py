from .models import Credito, Pago, PlanCredito
from apps.ventas.models import DetalleVenta
from .forms import RegistrarCreditoForm, RegistrarPagoForm

from io import BytesIO
import os

from django.views.generic import ListView,  DetailView, DeleteView, TemplateView
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Q, Prefetch
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages

from apps.usuarios.models import Actividad

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.template.loader import render_to_string

from datetime import date, timedelta
import json
from decimal import Decimal

# Create your views here.
@login_required
def CrearCreditoView(request):
    if request.method == 'POST':
        creditoForm = RegistrarCreditoForm(request.POST)
        if creditoForm.is_valid():
            credito = creditoForm.save(commit=False)
            credito.empresa = request.user.empresa
            credito.CalcularMontoCuota()
            credito.usuario = request.user
            credito.save()
            Actividad.objects.create(
                usuario=request.user,
                descripcion=f'Aprobaste un crédito a {credito.cliente.nombres} {credito.cliente.apellidos}'
            )
            return redirect('creditos:detalle_credito', credito.pk)
        else:
            # Mostrar los errores del formulario en un solo Swal
            for field, errors in creditoForm.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        creditoForm = RegistrarCreditoForm()

    return render(request, 'creditos/crear_credito.html', {"form": creditoForm})



class ListarCreditosView(LoginRequiredMixin, ListView):
    model = Credito
    template_name = 'creditos/listar_creditos.html'
    context_object_name = 'creditos'
    ordering = ["-pk"]
    paginate_by = 10

    def get_queryset(self):
        queryset = Credito.objects.filter(empresa = self.request.user.empresa)
        return queryset

        search = self.request.GET.get('search')
        estado = self.request.GET.get('estado')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        # 🔎 BUSCADOR
        if search:
            queryset = queryset.filter(
                Q(cliente__nombres__icontains=search) |
                Q(cliente__apellidos__icontains=search) |
                Q(cliente__dni__icontains=search)
            )

        # 📊 FILTRO POR ESTADO
        if estado:
            queryset = queryset.filter(estado=estado)

        # 📅 FILTRO POR FECHAS
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(
                fecha_inicio__range=[fecha_inicio, fecha_fin]
            )
        elif fecha_inicio:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
        elif fecha_fin:
            queryset = queryset.filter(fecha_inicio__lte=fecha_fin)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['estado'] = self.request.GET.get('estado', '')
        context['fecha_inicio'] = self.request.GET.get('fecha_inicio', '')
        context['fecha_fin'] = self.request.GET.get('fecha_fin', '')
        return context


class DetalleCreditoView(LoginRequiredMixin, DetailView):
    model = Credito
    template_name = 'creditos/detalle_credito.html'

    def get_queryset(self):
        return Credito.objects.filter(empresa = self.request.user.empresa)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        
        # Obteniendo todos los pagos del credito-pk
        pagos = Pago.objects.filter(credito = self.object)
        
        #Calculo de valores de pagos realizados
        totalPagado = sum(pago.monto for pago in pagos) + self.object.montoInicial

        #Calculo de deuda
        deuda_pendiente = Decimal(self.object.montoTotal - totalPagado)
        
        contexto['pagos'] = pagos
        contexto['total_pagado'] = totalPagado
        contexto['deuda_pendiente'] = deuda_pendiente

        return contexto


class EliminarCreditoView(LoginRequiredMixin, DeleteView):
    model = Credito
    success_url = reverse_lazy('creditos:listar_creditos')
    template_name = "creditos/eliminar.html"

    def get_queryset(self):
        return Credito.objects.filter(empresa = self.request.user.empresa)


class DashboardCreditosView(LoginRequiredMixin, TemplateView):
    template_name = 'creditos/dashboard.html'

    def get_queryset(self):
        return Credito.objects.filter(empresa = self.request.user.empresa)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoy = date.today()

        # Verificamos estado actualizado para todos los créditos
        for credito in Credito.objects.filter(empresa = self.request.user.empresa):
            credito.CompararMontoPagado()
            credito.verificar_estado()

        # Obtenemos créditos con estado finalizado, moroso o activo
        creditos = Credito.objects.filter(empresa = self.request.user.empresa).select_related('cliente', 'venta').prefetch_related(
            Prefetch('venta__detalles',  
                queryset=DetalleVenta.objects.select_related('producto'))
        )

        # Créditos con cuotas atrasadas: filtramos los créditos que tengan cuotas pendientes y fecha cuota pasada
        creditos_con_cuotas_atrasadas = []

        for credito in creditos:
            if credito.CompararMontoPagado() == False:
                cuotas_atrasadas = credito.verificar_pago_pendiente()
                if cuotas_atrasadas:
                    credito.num_cuotas_atrasadas = len(cuotas_atrasadas)  
                    creditos_con_cuotas_atrasadas.append(credito)

        
        # Créditos que ya finalizaron y están morosos (fecha_fin pasada y estado MOROSO)
        creditos_final_morosos = creditos.filter(fecha_fin__lt=hoy, estado='MOROSO')

        context['creditos_vencidos'] = list(creditos_final_morosos)
        context['creditos_cuotas_atrasadas'] = creditos_con_cuotas_atrasadas

        # El resto del contexto...
        context['total_creditos'] = creditos.count()
        context['creditos_activos'] = creditos.filter(estado='ACTIVO').count()
        context['creditos_morosos'] = creditos.filter(estado='MOROSO').count()
        context['creditos_finalizados'] = creditos.filter(estado='FINALIZADO').count()

        # Montos
        context['monto_total_prestado'] = creditos.aggregate(total=Sum('montoTotal'))['total'] or 0
        context['monto_por_cobrar'] = creditos.filter(
            Q(estado='ACTIVO') | Q(estado='MOROSO')
        ).aggregate(total=Sum('montoTotal'))['total'] or 0

        # Créditos próximos a vencer
        context['creditos_proximos_vencer'] = creditos.filter(
            fecha_fin__range=[hoy, hoy + timedelta(days=30)],
            estado='ACTIVO'
        ).order_by('fecha_fin')

        # Distribución tipo pago
        distribucion = list(creditos.values('tipo_pago').annotate(
            total=Count('id'),
            monto_total=Sum('montoTotal')
        ))
        context['distribucion_tipo_pago'] = json.dumps(distribucion, cls=DjangoJSONEncoder)

        # Últimos créditos aprobados
        context['ultimos_creditos'] = creditos.order_by('-fecha_inicio')[:6]

        return context


def obtener_planes_credito(request, producto_id):
    planes = PlanCredito.objects.filter(producto_id=producto_id, empresa= request.user.empresa).select_related('plazo').order_by('plazo__meses')
    
    data = [
        {
            'plazo': plan.plazo.meses,
            'precio': float(plan.precio),
        }
        for plan in planes
    ]

    return JsonResponse(data, safe=False)

# PAGOS
@login_required
def RegistrarPagoView(request, pk):
    credito = get_object_or_404(Credito, pk=pk)
    
    if request.method == 'POST':
        PagoForm = RegistrarPagoForm(request.POST)
        
        if PagoForm.is_valid():
            pago = PagoForm.save(commit=False)
            pago.credito = credito
            pago.usuario = request.user
            pago.empresa = request.user.empresa
            pago.cuota = Pago.objects.filter(credito=pk).count() + 1
            credito.cuotas_pagadas = pago.cuota

            saldo_pendiente = Decimal(credito.montoTotal - credito.CalcularMontoPagado())

            if pago.monto <= saldo_pendiente:
                pago.save()
                Actividad.objects.create(
                    usuario=request.user,
                    descripcion=f'Se registró un pago de ${pago.monto}'
                )

                # 🔄 Actualizar estado del crédito
                credito.CompararMontoPagado()
                credito.verificar_estado()

                # 🎯 Mensaje personalizado con sweetalert via messages
                if saldo_pendiente - pago.monto == 0:
                    messages.success(request, '✅ ¡Deuda cancelada por completo! Crédito finalizado.')
                else:
                    messages.success(request, f'✅ Pago de ${pago.monto} registrado correctamente.')

                return redirect('creditos:detalle_credito', pk=credito.pk)
            else:
                PagoForm.add_error('monto', '🚫 El monto del pago excede el saldo pendiente.')

        # Capturar errores y enviarlos con messages.error
        for field, errors in PagoForm.errors.items():
            for error in errors:
                messages.error(request, f"⚠️ {error}")

    else:
        cuota_inicial = Pago.objects.filter(credito=pk).count() + 1
        PagoForm = RegistrarPagoForm(initial={'cuota': cuota_inicial})

    contexto = {
        'form': PagoForm,
        'credito': credito,
    }

    return render(request, 'pagos/registrar_pago.html', contexto)


def calendario(request, credito_id):
    # Obtiene el crédito del cliente
    credito = get_object_or_404(Credito, id=credito_id, empresa=request.user.empresa)    
    # Genera las fechas de pago
    fechas_pago = credito.generar_fechas_pago()
    
    # Obtenemos los pagos realizados
    pagos_realizados = Pago.objects.filter(credito=credito).values_list('cuota', flat=True)
    
    eventos = []
    hoy = date.today()

    # Generamos los eventos para el calendario
    for pago in fechas_pago:
        cuota_num = pago['cuota']
        fecha_pago = pago['fecha']
        
        # Determinamos el color del evento según el estado
        if cuota_num in pagos_realizados:
            color = 'green'  # Pago realizado
        elif hoy > fecha_pago:
            color = 'red'  # Pago vencido
        else:
            color = 'blue'  # Pago pendiente
            
        eventos.append({
            'title': f'Cuota {cuota_num}: {credito.montoCuota} USD',
            'start': fecha_pago.strftime('%Y-%m-%d'),
            'color': color,
            'description': f'Fecha de pago: {fecha_pago}',
        })

    # Convertimos eventos a formato JSON
    eventos_json = json.dumps(eventos)
    
    return render(request, 'creditos/calendario.html', {'credito': credito, 'eventos_json': eventos_json})


#Generacion de comprobante de pago
@login_required
def generar_comprobante_pago(request, pk):
    # Obtener los datos necesarios
    pago = get_object_or_404(Pago, pk=pk, empresa = request.user.empresa)
    credito = pago.credito
    cliente = credito.cliente
    monto_pagado = credito.CalcularMontoPagado()
    
    # Renderizar los datos a la plantilla
    return render(request, 'pagos/comprobante_pago.html', {
        'pago': pago,
        'credito': credito,
        'cliente': cliente,
        'usuario': request.user.username,
        'monto_pagado_total' : monto_pagado,
    })

# Generacion del contrato - PDF
@login_required
def GenerarContrato(request, pk):
    # Datos de la empresa
    empresa = request.user.empresa.nombre_comercial
    #propietario = 'Roberto Oña y Blanca Chango'
    correo = request.user.empresa.correo
    ruc = request.user.empresa.ruc
    telefono = request.user.empresa.telefono
    direccion = request.user.empresa.direccion

    # Crear buffer PDF
    buffer = BytesIO()

    # Obtener el crédito
    credito = get_object_or_404(Credito, pk=pk, empresa=request.user.empresa)

    # Canvas
    logo_path = os.path.join(settings.MEDIA_ROOT, 'hogar.PNG')
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Courier", 10)

    # Logo
    try:
        p.drawImage(
            logo_path,
            inch, 
            9.5 * inch,   # mueve un poco la posición vertical
            width=2.5 * inch,  # más ancho
            height=1.5 * inch, # más alto
            preserveAspectRatio=True,
            mask='auto'
        )

    except Exception as e:
        print(f"Error al cargar el logo: {e}")

    # Obtener tamaño de página
    width, height = letter

    # === MARGEN SUPERIOR ===
    TOP = height - 0.60 * inch    # ajusta aquí (más grande = más abajo)

    # Encabezado
    p.setFont("Courier-Bold", 12)
    p.drawString(4.5 * inch, TOP, "Contrato de Crédito")

    p.setFont("Courier", 10)
    p.drawString(4.5 * inch, TOP - 0.25 * inch, f"Orden de crédito #{credito.pk}")
    p.drawString(4.5 * inch, TOP - 0.5 * inch, f"Fecha de orden: {credito.fecha_inicio.strftime('%d de %B de %Y')}")


    # Datos empresa
    p.setFont("Courier-Bold", 10)
    p.drawString(inch, 9.5 * inch, "Datos de la empresa")
    p.setFont("Courier", 10)
    p.drawString(inch, 9.25 * inch, f"Nombre Comercial: {empresa}")
    p.drawString(inch, 9 * inch, f"RUC: {ruc}")
    p.drawString(inch, 8.75 * inch, f"Correo: {correo}")
    p.drawString(inch, 8.5 * inch, f"Teléfono: {telefono}")
    p.drawString(inch, 8.25 * inch, direccion)
    p.line(inch, 7.8 * inch, 4 * inch, 7.8 * inch)

    # Datos cliente
    p.setFont("Courier-Bold", 10)
    p.drawString(4.5 * inch, 9.5 * inch, "Datos cliente")
    p.setFont("Courier", 10)
    p.drawString(4.5 * inch, 9.25 * inch, f"Cliente: {credito.cliente.nombres} {credito.cliente.apellidos}")
    p.drawString(4.5 * inch, 9.0 * inch, f"Cédula: {credito.cliente.dni}")
    p.drawString(4.5 * inch, 8.75 * inch, f"Correo: {credito.cliente.correo}")
    p.drawString(4.5 * inch, 8.50 * inch, f"Teléfono: {credito.cliente.telefono}")
    p.drawString(4.5 * inch, 8.25 * inch, f"Dirección: {credito.cliente.direccion}, {credito.cliente.ciudad}")
    p.line(4.5 * inch, 7.8 * inch, 7.5 * inch, 7.8 * inch)

    # Monto total de la deuda - texto destacado
    p.setFont("Courier-Bold", 12)
    p.drawString(inch, 6.8 * inch, f"Monto total de la deuda: ${credito.montoTotal:.2f}")
    p.drawString(inch, 6.6  * inch, f"Valor de Entrada: ${credito.montoInicial:.2f}")
    
    # Tabla con detalle de cuotas
    fechas_pago = credito.generar_fechas_pago()
    data_cuotas = [["N° Cuota", "Fecha de Pago", "Monto"]]
    for cuota in fechas_pago:
        nro = cuota["cuota"]
        fecha = cuota["fecha"].strftime('%d/%m/%Y')
        monto = f"${credito.montoCuota:.2f}"
        data_cuotas.append([str(nro), fecha, monto])

    col_widths_cuotas = [1.0 * inch, 2.5 * inch, 2.5 * inch]
    tabla_cuotas = Table(data_cuotas, colWidths=col_widths_cuotas)
    tabla_cuotas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    w, h = tabla_cuotas.wrapOn(p, 6 * inch, 6 * inch)
    tabla_cuotas.drawOn(p, inch, 6.2 * inch - h) 

    # Términos y condiciones 
    y_actual = 6.4 * inch - h - 0.6 * inch  # un pequeño espacio tras la tabla
    p.setFont("Courier-Bold", 10)
    p.drawString(inch, y_actual, "Términos y Condiciones:")

    p.setFont("Courier", 8)
    p.drawString(inch, y_actual - 0.2 * inch, "1. El cliente se compromete a pagar las cuotas en las fechas establecidas.")
    p.drawString(inch, y_actual - 0.35 * inch, "2. En caso de retraso en los pagos se aplicará un pequeño recargo por cada día de atraso.")
    p.drawString(inch, y_actual - 0.50 * inch, "3. El cliente autoriza el tratamiento de sus datos personales para fines administrativos y de cobro.")
    p.drawString(inch, y_actual - 0.65 * inch, "4. El cliente deberá informar si cambia de número de teléfono para poder recibir recordatorios del pago.")
    p.drawString(inch, y_actual - 0.95 * inch, "El cliente declara haber leído y aceptado los términos de este acuerdo.")

    # Firmas
    """
    y_firmas = y_actual - 1.0 * inch
    p.setFont("Courier", 10)
    p.drawString(inch, y_firmas, "____________________________")
    p.drawString(4 * inch, y_firmas, "____________________________")

    p.drawString(inch, y_firmas - 0.2 * inch, credito.cliente.nombres + " " + credito.cliente.apellidos)
    p.drawString(4 * inch, y_firmas - 0.2 * inch, empresa)
    """

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="credito_{credito.pk}_{credito.cliente}.pdf"'
    return response