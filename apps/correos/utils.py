from io import BytesIO
from django.core.mail import send_mail
from datetime import datetime, timedelta, date
from .models import EstadoEnvioCorreo
from apps.creditos.models import Credito, Pago
from core.settings import EMAIL_HOST_USER
from django.conf import settings


def generar_mensaje_html(cliente, cuotas_pendientes, monto):
    
    cuotas_html = "".join([
        f'''
        <div class="cuota-item">
            <div class="cuota-numero">Cuota {num}</div>
            <div class="cuota-fecha">📅 {fecha}</div>
        </div>
        ''' for num, fecha in cuotas_pendientes
    ])

    mensaje_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recordatorio de Cuotas</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }}
            
            .email-container {{
                max-width: 650px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                color: white;
                padding: 30px;
                text-align: center;
                position: relative;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="white" opacity="0.1"><polygon points="0,0 1000,0 1000,100"/></svg>');
                background-size: cover;
            }}
            
            .header h1 {{
                font-size: 28px;
                margin-bottom: 10px;
                position: relative;
                z-index: 1;
            }}
            
            .header-icon {{
                font-size: 48px;
                margin-bottom: 15px;
                display: block;
                position: relative;
                z-index: 1;
            }}
            
            .content {{
                padding: 40px;
            }}
            
            .greeting {{
                font-size: 18px;
                color: #2c3e50;
                margin-bottom: 25px;
                font-weight: 600;
            }}
            
            .message {{
                font-size: 16px;
                color: #5a6c7d;
                margin-bottom: 30px;
                line-height: 1.8;
            }}
            
            .cuotas-container {{
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                margin: 25px 0;
                border-left: 5px solid #ff6b6b;
            }}
            
            .cuotas-title {{
                font-size: 18px;
                color: #2c3e50;
                margin-bottom: 20px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .cuota-item {{
                background: white;
                border-radius: 10px;
                padding: 15px 20px;
                margin-bottom: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                border-left: 4px solid #ff6b6b;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: transform 0.2s ease;
            }}
            
            .cuota-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
            
            .cuota-item:last-child {{
                margin-bottom: 0;
            }}
            
            .cuota-numero {{
                font-weight: 600;
                color: #2c3e50;
                font-size: 16px;
            }}
            
            .cuota-fecha {{
                color: #7f8c8d;
                font-size: 14px;
            }}
            
            .monto-container {{
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                margin: 25px 0;
                box-shadow: 0 8px 16px rgba(76, 175, 80, 0.3);
            }}
            
            .monto-label {{
                font-size: 16px;
                margin-bottom: 8px;
                opacity: 0.9;
            }}
            
            .monto-valor {{
                font-size: 32px;
                font-weight: bold;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }}
            
            .alert-box {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 10px;
                padding: 20px;
                margin: 25px 0;
                border-left: 5px solid #fdcb6e;
            }}
            
            .alert-text {{
                color: #856404;
                font-size: 16px;
                font-weight: 500;
                margin: 0;
            }}
            
            .footer {{
                background: #2c3e50;
                color: white;
                padding: 25px;
                text-align: center;
            }}
            
            .footer-text {{
                font-size: 14px;
                opacity: 0.8;
                margin-bottom: 10px;
            }}
            
            .footer-brand {{
                font-size: 18px;
                font-weight: 600;
                color: #ff6b6b;
            }}
            
            .divider {{
                height: 2px;
                background: linear-gradient(to right, #ff6b6b, #ee5a24);
                margin: 30px 0;
                border-radius: 2px;
            }}
            
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 15px;
                }}
                
                .header, .content, .footer {{
                    padding: 20px;
                }}
                
                .cuota-item {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 8px;
                }}
                
                .monto-valor {{
                    font-size: 28px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <span class="header-icon">⚠️</span>
                <h1>Recordatorio de Cuotas Pendientes</h1>
            </div>
            
            <div class="content">
                <div class="greeting">
                    Estimado/a {cliente.nombres} {cliente.apellidos}
                </div>
                
                <div class="message">
                    Esperamos que se encuentre bien. Le escribimos para recordarle que tiene cuotas pendientes de pago en su crédito.
                </div>
                
                <div class="cuotas-container">
                    <div class="cuotas-title">
                        📋 Cuotas Pendientes
                    </div>
                    {cuotas_html}
                </div>
                
                <div class="monto-container">
                    <div class="monto-label">💰 Monto por cuota</div>
                    <div class="monto-valor">${monto:.2f}</div>
                </div>
                
                <div class="alert-box">
                    <p class="alert-text">
                        ⏰ Por favor, realice los pagos lo antes posible para evitar inconvenientes y mantener su historial crediticio en buen estado.
                    </p>
                </div>
                
                <div class="divider"></div>
                
                <div class="message">
                    Agradecemos su atención y quedamos a su disposición para cualquier consulta.
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-text">
                    Este es un mensaje automático del sistema
                </div>
                <div class="footer-brand">
                    🏦 Sistema de Créditos
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return mensaje_html


def enviar_recordatorios_pago(empresa):
    hoy = date.today()
    manana = hoy + timedelta(days=1)

    # Filtrar todos los créditos con deuda pendiente, sin importar el estado
    creditos = Credito.objects.filter(empresa = empresa)

    for credito in creditos:
        if credito.deuda_pendiente <= 0:
            continue  # No debe nada, lo saltamos

        fechas_pago = credito.generar_fechas_pago()
        pagos_realizados = Pago.objects.filter(empresa=empresa).values_list('cuota', flat=True)

        cuotas_pendientes = []

        for pago in fechas_pago:
            cuota_num = pago['cuota']
            fecha_pago = pago['fecha']

            if cuota_num not in pagos_realizados:
                # Si la cuota ya venció o vence mañana, se notifica
                if fecha_pago <= manana:
                    cuotas_pendientes.append((cuota_num, fecha_pago))

        if cuotas_pendientes:
            cliente = credito.cliente
            correo = cliente.correo
            monto = credito.montoCuota

            mensaje_html = generar_mensaje_html(cliente, cuotas_pendientes, monto)

            if credito.esta_vencido:
                asunto = '⚠️ Su crédito está vencido y tiene cuotas pendientes'
            else:
                asunto = '📢 Recordatorio de cuotas pendientes de su crédito'

            try:
                send_mail(
                    subject=asunto,
                    message='',  
                    from_email=empresa.correo,
                    recipient_list=[correo],
                    fail_silently=False,
                    html_message=mensaje_html,  
                )
                print(f"✅ Correo enviado a {correo}")
            except Exception as e:
                print(f"❌ Error al enviar a {correo}: {e}")


def enviar_recordatorios_pago_una_vez_al_dia():
    estado, creado = EstadoEnvioCorreo.objects.get_or_create(id=1)
    hoy = date.today()

    if estado.ultima_ejecucion != hoy:
        print(" ✅ Enviando recordatorios automáticos de pago... ")
        enviar_recordatorios_pago()
        estado.ultima_ejecucion = hoy
        estado.exito = True
        estado.save()
    else:
        print("⚠️ Recordatorios ya enviados hoy. ")