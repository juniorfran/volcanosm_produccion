from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from Transacciones.wompi_connect import authenticate_wompi
from Transacciones.wompi_consulta import make_wompi_get_request
from Transacciones.wompi_envio import create_payment_link
from Tours.models import ImagenTour, Resena, Tour, Reserva
from Tours.models import EnlacePagoTour
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from Internet.models import Accesos, Tipos
import csv
import pandas as pd
from django.http import HttpResponse


Client_id = settings.CLIENT_ID
Client_secret = settings.CLIENT_SECRET

@login_required
def index_utilidades(request):
    
    return render(request, 'base_utilities.html')


def consultar_enlace_pago(enlace_pago_id, client_id, client_secret):
    # Autenticar con Wompi y obtener el token
    access_token = authenticate_wompi(client_id, client_secret)

    if not access_token:
        print("Error de autenticación con Wompi.")
        return None

    # Utilizar la función make_wompi_get_request para realizar la solicitud GET
    endpoint = f"EnlacePago/{enlace_pago_id}"
    enlace_pago_info = make_wompi_get_request(endpoint, access_token)

    if enlace_pago_info:
        # Imprimir la información del enlace de pago
        print("Información del enlace de pago:")
        print(enlace_pago_info)
        return enlace_pago_info
    else:
        print("Error al obtener información del enlace de pago.")
        return None

# Ejemplo de uso
# enlace_pago_id = "1072404"
# consultar_enlace_pago(enlace_pago_id, Client_id, Client_secret)


@login_required
def consultar_detalle (request):
    user = request.user
    if request.method == 'POST':
        
        numero_reserva = request.POST.get('numero_reserva')
        try:
            # Filtrar las reservas que coinciden con los últimos 4 dígitos
            reservas = Reserva.objects.filter(
                Q(codigo_reserva__endswith=numero_reserva) |
                Q(codigo_reserva=numero_reserva)
            )

            if reservas.exists():
                # Tomar la primera reserva encontrada
                reserva = reservas.first()

                # Buscar enlace relacionado a la reserva
                enlace_pago = EnlacePagoTour.objects.filter(reserva=reserva).first()

                # Si se encuentra un enlace, consultar la información
                if enlace_pago:
                    enlace_pago_info = consultar_enlace_pago(enlace_pago.idEnlace, Client_id, Client_secret)
                    if enlace_pago_info:
                        return render(request, 'detalle.html', {'enlace_pago': enlace_pago_info, 'reserva': reserva})
                    else:
                        return render(request, 'detalle.html', {'error_message': 'Error al obtener información del enlace de pago.'})
                else:
                    return render(request, 'detalle.html', {'error_message': 'No se encontró un enlace de pago para la reserva.'})
            else:
                return render(request, 'detalle.html', {'error_message': 'Reserva no encontrada.'})

        except Reserva.DoesNotExist:
            return render(request, 'detalle.html', {'error_message': 'Enlace de pago no encontrada.'})
    else:
        return render(request, 'detalle.html', {})

def upload_data(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if file.name.endswith('.csv'):
            data = csv.DictReader(file.read().decode('utf-8').splitlines())
        elif file.name.endswith('.xlsx'):
            data = pd.read_excel(file)
            data = data.to_dict('records')
        else:
            messages.error(request, 'Formato de archivo no válido. Solo se admiten archivos CSV o Excel.')
            return redirect('upload_data')
        
        for row in data:
            tipo_acceso_id = row.get('tipo_acceso_id')  # Obtener el ID del tipo de acceso
            tipo_acceso_instance = Tipos.objects.get(id=tipo_acceso_id)  # Obtener la instancia del tipo de acceso
            
            acceso = Accesos(
                usuario=row.get('usuario'),
                password=row.get('password'),
                descripcion=row.get('descripcion'),
                cant_usuarios=row.get('cant_usuarios'),
                acceso_tipo=tipo_acceso_instance,  # Asignar la instancia del tipo de acceso
                fecha_expiracion=row.get('fecha_expiracion'),
                estado=row.get('estado')
            )
            acceso.save()
        
        messages.success(request, 'Los datos se han cargado correctamente.')
        return redirect('utilidades:upload_data')
    return render(request, 'internet/upload_data.html')



###################################################################################################################
            # VISTAS PARA MANEJAR EL ROUTER MIKROTIK #
###################################################################################################################

from librouteros import connect
from librouteros.query import Key
import ssl
from functools import partial
import librouteros as ros
from Internet.models import MikrotikConfig
import socket

def connect_to_router(router_ip, username, password, use_ssl=False):
    # Establish a TCP connection to the Cloudflare tunnel
    tunnel_url = "mikrotik.dcobranza.com"
    tunnel_port = 8728

    sock = socket.create_connection((tunnel_url, tunnel_port))

    # Create a ROS API connection object
    api = ros.ApiRos(sock)

    # Login to the router
    api.login(username, password)

    return api

def mikrotik_login(request):
    if request.method == 'POST':
        router_url = request.POST.get('router_url')
        username = request.POST.get('username')
        password = request.POST.get('password')
        use_ssl = request.POST.get('use_ssl') == 'on'

        try:
            api = connect_to_router(router_url, username, password, use_ssl)

            request.session['router_url'] = router_url
            request.session['username'] = username
            request.session['password'] = password
            request.session['use_ssl'] = use_ssl

            return redirect('utilidades:mikrotik_interfaces')

        except Exception as e:
            return render(request, 'internet/mikrotik_login.html', {'error': f'Error: {str(e)}'})

    return render(request, 'internet/mikrotik_login.html')

# def connect_to_router(router_ip, username, password, use_ssl=False):
#     if use_ssl:
#         api = ros.connect_ssl(router_ip, username=username, password=password)
#     else:
#         api = ros.connect(router_ip, username=username, password=password)
#     return api


# def mikrotik_login(request):
#     if request.method == 'POST':
#         router_url = request.POST.get('router_url')
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         use_ssl = request.POST.get('use_ssl') == 'on'

#         try:
#             if use_ssl:
#                 ctx = ssl.create_default_context()
#                 ctx.check_hostname = False
#                 ctx.set_ciphers('ADH:@SECLEVEL=0')
#                 ssl_wrapper = partial(ctx.wrap_socket, server_hostname=router_url)
#                 api = connect(
#                     username=username,
#                     password=password,
#                     host=router_url,
#                     ssl_wrapper=ssl_wrapper,
#                     port=8729  # Asegúrate de usar el puerto correcto aquí
#                 )
#             else:
#                 api = connect(
#                     username=username,
#                     password=password,
#                     host=router_url,
#                     port=8728 # Asegúrate de usar el puerto correcto aquí
#                 )

#             request.session['router_url'] = router_url
#             request.session['username'] = username
#             request.session['password'] = password
#             request.session['use_ssl'] = use_ssl

#             return redirect('utilidades:mikrotik_interfaces')

#         except Exception as e:
#             return render(request, 'internet/mikrotik_login.html', {'error': f'Error: {str(e)}'})

#     return render(request, 'internet/mikrotik_login.html')



def mikrotik_interfaces(request):
    router_ip = request.session.get('router_ip')
    username = request.session.get('username')
    password = request.session.get('password')
    use_ssl = request.session.get('use_ssl')

    if not all([router_ip, username, password]):
        return redirect('utilidades:mikrotik_manager')

    try:
        if use_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.set_ciphers('ADH:@SECLEVEL=0')
            ssl_wrapper = partial(ctx.wrap_socket, server_hostname=router_ip)
            api = connect(
                username=username,
                password=password,
                host=router_ip,
                ssl_wrapper=ssl_wrapper,
                port=8729
            )
        else:
            api = connect(
                username=username,
                password=password,
                host=router_ip,
            )

        interfaces = list(api('/interface/print'))

        active_interfaces = [iface for iface in interfaces if 'disabled' not in iface or not iface['disabled']]
        inactive_interfaces = [iface for iface in interfaces if 'disabled' in iface and iface['disabled']]

        context = {
            'active_interfaces': active_interfaces,
            'inactive_interfaces': inactive_interfaces,
            'error': None,
            'is_logged_in': True  # Indica que se ha iniciado sesión en el router MikroTik
        }
        return render(request, 'internet/mikrotik_manager.html', context)

    except Exception as e:
        return render(request, 'internet/mikrotik_manager.html', {'error': f'Error: {str(e)}'})
    
    
def mikrotik_status(request):
    router_ip = request.session.get('router_ip')
    username = request.session.get('username')
    password = request.session.get('password')
    use_ssl = request.session.get('use_ssl')

    if not all([router_ip, username, password]):
        return redirect('mikrotik_manager')

    try:
        if use_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.set_ciphers('ADH:@SECLEVEL=0')
            ssl_wrapper = partial(ctx.wrap_socket, server_hostname=router_ip)
            api = connect(
                username=username,
                password=password,
                host=router_ip,
                ssl_wrapper=ssl_wrapper,
                port=8729
            )
        else:
            api = connect(
                username=username,
                password=password,
                host=router_ip,
            )

        interfaces = list(api.path('interface').select(
            Key('name'),
            Key('type'),
            Key('tx-byte'),
            Key('rx-byte'),
            Key('running'),
            Key('disabled')
        ))

        ip_addresses = list(api.path('ip', 'address').select(
            Key('interface'),
            Key('address')
        ))

        dhcp_servers = list(api.path('ip', 'dhcp-server').select(
            Key('name'),
            Key('interface'),
            Key('lease-time'),
            Key('address-pool'),
            Key('dynamic'),
            Key('disabled')
        ))

        dhcp_leases = list(api.path('ip', 'dhcp-server', 'lease').select(
            Key('address'),
            Key('mac-address'),
            Key('expires-after')
        ))

        context = {
            'interfaces': interfaces,
            'ip_addresses': ip_addresses,
            'dhcp_servers': dhcp_servers,
            'dhcp_leases': dhcp_leases,
            'error': None,
            'is_logged_in': True  # Indica que se ha iniciado sesión en el router MikroTik
        }
        return render(request, 'internet/mikrotik_status.html', context)

    except Exception as e:
        return render(request, 'internet/mikrotik_status.html', {'error': f'Error: {str(e)}'})




def create_hotspot_user(request):
    if request.method == 'POST':
        router_ip = request.session.get('router_ip')
        username = request.session.get('username')
        password = request.session.get('password')
        use_ssl = request.session.get('use_ssl', False)

        try:
            api = connect_to_router(router_ip, username, password, use_ssl)

            # Obtener datos del formulario
            server_id = request.POST.get('server_id')
            username = request.POST.get('username')
            password = request.POST.get('password')
            profile = request.POST.get('profile')

            # Crear el usuario del hotspot
            # api(cmd='/ip/hotspot/user/add', 
            #     server=server_id, 
            #     name=username, 
            #     password=password, 
            #     profile=profile)
            
            api.path('/ip/hotspot/user').add(
                server=server_id, 
                name=username, 
                password=password, 
                profile=profile
            )

            return redirect('utilidades:list_hotspot_user')

        except Exception as e:
            error_message = f'Error al crear usuario de hotspot: {str(e)}'
            # Renderizar de nuevo el formulario con el mensaje de error
            return render(request, 'internet/hostpot/create_hotspot_user.html', {'error': error_message, 'servers': servers, 'profiles': profiles, 'is_logged_in': True})

    else:
        router_ip = request.session.get('router_ip')
        username = request.session.get('username')
        password = request.session.get('password')
        use_ssl = request.session.get('use_ssl', False)

        try:
            api = connect_to_router(router_ip, username, password, use_ssl)

            # Obtener lista de servidores de hotspot para el selector

            servers = api('/ip/hotspot/print')

            # Obtener lista de perfiles de usuarios de hotspot para el selector
            profiles = api('/ip/hotspot/profile/print')

            context = {
                'servers': servers,
                'profiles': profiles,
                'is_logged_in': True,
            }

        except Exception as e:
            context = {
                'error': f'Error al obtener datos del router: {str(e)}',
            }

        return render(request, 'internet/hostpot/create_hotspot_user.html', context)


def create_hotspot_user_profile(request):
    router_ip = request.session.get('router_ip')
    username = request.session.get('username')
    password = request.session.get('password')
    use_ssl = request.session.get('use_ssl', False)
    
    api = connect_to_router(router_ip, username, password, use_ssl)
    #obetener los pool
    pools1 = api('/ip/pool/print')
    
    if request.method == 'POST':
        router_ip = request.session.get('router_ip')
        username = request.session.get('username')
        password = request.session.get('password')
        use_ssl = request.session.get('use_ssl', False)
        
        try:
            api = connect_to_router(router_ip, username, password, use_ssl)

            # Obtener datos del formulario
            name = request.POST.get('name')
            rate_limit = request.POST.get('rate_limit')
            session_timeout = request.POST.get('session_timeout')
            mac_timeout = request.POST.get('mac_timeout')
            address_pool = request.POST.get('address_pool')

            api.path('/ip/hotspot/user/profile').add(**{
                'name': name,
                'address-pool': address_pool,
                'session-timeout': session_timeout,
                'rate-limit': rate_limit,
                'mac-cookie-timeout': mac_timeout
            })
                        
            return redirect('utilidades:list_hotspot_user_profile')

        except Exception as e:
            error_message = f'Error al crear perfil de usuario de hotspot: {str(e)}'
            # Renderizar de nuevo el formulario con el mensaje de error
            return render(request, 'internet/hostpot/create_hotspot_user_profile.html', {'error': error_message, 'is_logged_in': True})

    else:
        return render(request, 'internet/hostpot/create_hotspot_user_profile.html', {'pools':pools1, 'is_logged_in': True})

def list_hotspot_users(request):
    router_ip = request.session.get('router_ip')
    username = request.session.get('username')
    password = request.session.get('password')
    use_ssl = request.session.get('use_ssl', False)
    
    api = connect_to_router(router_ip, username, password, use_ssl)
    
    # Obtener lista de perfiles de usuarios de hotspot para el selector
    #profiles = api('/ip/hotspot/user/profile/print')
    
    users = list(api.path('/ip/hotspot/user').select(
        #Key('id'),
        Key('server'),
        Key('name'),
        Key('address'),
        Key('profile'),
        Key('updtime'),
    ))

    
    context={
        'users':users,
        'is_logged_in': True,
    }
    
    return render(request, 'internet/hostpot/list_hotspot_user.html', context)


def list_hotspot_user_profile(request):
    router_ip = request.session.get('router_ip')
    username = request.session.get('username')
    password = request.session.get('password')
    use_ssl = request.session.get('use_ssl', False)
    
    api = connect_to_router(router_ip, username, password, use_ssl)
    
    # Obtener lista de perfiles de usuarios de hotspot para el selector
    #profiles = api('/ip/hotspot/user/profile/print')
    
    profiles = list(api.path('/ip/hotspot/user/profile').select(
        #Key('id'),
        Key('name'),
        Key('address-pool'),
        Key('session-timeout'),
        Key('rate-limit'),
        Key('mac-cookie-timeout'),
        Key('keepalive-timeout')
    ))

    
    context={
        'profiles':profiles,
        'is_logged_in': True,
    }
    
    return render(request, 'internet/hostpot/list_hotspot_user_profile.html', context)

def create_mikrotik_config(request):
    if request.method == 'POST':
        servidor = request.POST.get('servidor')
        usuario = request.POST.get('usuario')
        password = request.POST.get('password')
        puerto = request.POST.get('puerto')
        use_ssl = request.POST.get('use_ssl') == 'on'  # Convertir el valor de 'on' a True

        MikrotikConfig.objects.create(
            servidor=servidor,
            usuario=usuario,
            password=password,
            puerto=puerto,
            use_ssl=use_ssl,
        )

        return redirect('utilidades:create_mikrotik_config')  # Redirigir a la misma vista para ver la lista actualizada

    configs = MikrotikConfig.objects.all()  # Obtener todas las configuraciones

    return render(request, 'internet/config_mikrotik/create_mikrotik_config.html', {'configs': configs, 'is_logged_in': True,})