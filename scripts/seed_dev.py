# -*- coding: utf-8 -*-
"""Carga datos de demo para desarrollo (Volcano). Idempotente por sección.

Ejecutar:  python manage.py shell < scripts/seed_dev.py
Usa bulk_create en modelos cuyo save() hace red (Azure/email) para no romper.
"""
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User

now = timezone.now()
fin = now + timedelta(days=365)
admin = User.objects.filter(is_superuser=True).first()


def section(label, fn):
    try:
        fn()
        print("OK  -", label)
    except Exception as e:
        print("ERR -", label, "::", repr(e)[:160])


# ----------------- Configuraciones (sitio público) -----------------
def seed_config():
    from Configuraciones.models import (Barra_Principal, Contacts, General_Description,
        Direccionamiento, CarruselInicio, Services_Bar, Team_bar, Urls_info, Urls_interes, wompi_config)
    if not Barra_Principal.objects.exists():
        Barra_Principal.objects.create(email_contacto="info@volcanosm.com", numero_contacto="+503 2660-0000",
            url_facebook="https://facebook.com/volcanosm", url_twitter="#", url_linkedin="#",
            url_instagram="https://instagram.com/volcanosm", url_youtube="#")
    if not Contacts.objects.exists():
        Contacts.objects.create(contact_email="info@volcanosm.com", contact_phone="+503 2660-0000",
            addres="Volcán de San Miguel (Chaparrastique), San Miguel, El Salvador")
    if not General_Description.objects.exists():
        General_Description.objects.create(titulo_largo="Al Pie del Volcán", titulo_corto="Volcano",
            medio_titulo="Turismo de aventura", descripcion_larga="Vive la aventura en el Volcán de San Miguel: tours, camping y caminatas.",
            descripcion_corta="Turismo en el Volcán de San Miguel")
    if not Direccionamiento.objects.exists():
        Direccionamiento.objects.create(nombre="Ubicación principal", imagen="", url_azure="")
    if not CarruselInicio.objects.exists():
        CarruselInicio.objects.bulk_create([
            CarruselInicio(titulo=t, contenido=c, imagen="", imagen_url="", url_boton="#", texto_boton="Ver más")
            for t, c in [("Conquista el Chaparrastique", "Caminatas guiadas a la cima"),
                         ("Acampa bajo las estrellas", "Zona de camping equipada"),
                         ("Aventura en familia", "Senderismo para todos")]])
    if not Services_Bar.objects.exists():
        Services_Bar.objects.bulk_create([
            Services_Bar(services_visible=True, services_ico="", imagen_url="", services_ico_tag="fa fa-mountain",
                         services_name=n, services_description=d)
            for n, d in [("Tours guiados", "Ascensos seguros al volcán"),
                         ("Camping", "Zona equipada al pie del volcán"),
                         ("Caminatas", "Senderos para todo nivel"),
                         ("Alquiler de equipo", "Tiendas, colchonetas y hamacas")]])
    if not Team_bar.objects.exists():
        Team_bar.objects.bulk_create([
            Team_bar(team_image="", imagen_url="", team_nombre=n, team_job=j,
                     url_facebook="#", url_twitter="#", url_linkedin="#", url_instagram="#")
            for n, j in [("Carlos Méndez", "Guía principal"), ("Ana Rivera", "Coordinadora de camping"),
                         ("Luis Torres", "Guía de senderismo"), ("María López", "Atención al cliente")]])
    if not Urls_info.objects.exists():
        for t, u in [("Inicio", "/"), ("Tours", "/tours/"), ("Servicios", "/servicios/servicios/"),
                     ("Nosotros", "/nosotros/"), ("Contacto", "/contactanos/contact/")]:
            Urls_info.objects.create(title=t, url=u)
    if not Urls_interes.objects.exists():
        for t, u in [("Facebook", "https://facebook.com/volcanosm"),
                     ("Instagram", "https://instagram.com/volcanosm"),
                     ("MARN El Salvador", "https://www.marn.gob.sv/")]:
            Urls_interes.objects.create(title=t, url=u)
    if not wompi_config.objects.exists():
        wompi_config.objects.create(cuenta="Volcano DEV", client_id="dev-client-id", client_secret="dev-secret")


# ----------------- Tours -----------------
def seed_tours():
    from Tours.models import TipoTour, Tour, Resena
    if Tour.objects.exists():
        return
    aventura, _ = TipoTour.objects.get_or_create(nombre="Aventura")
    familiar, _ = TipoTour.objects.get_or_create(nombre="Familiar")
    data = [
        ("Caminata al cráter del Volcán de San Miguel", Decimal("35.00"), Decimal("20.00"), 8, True, aventura),
        ("Camping nocturno en el Chaparrastique", Decimal("45.00"), Decimal("25.00"), 24, False, aventura),
        ("Senderismo y avistamiento de naturaleza", Decimal("25.00"), Decimal("15.00"), 5, True, familiar),
        ("Tour fotográfico al amanecer", Decimal("30.00"), Decimal("18.00"), 6, True, aventura),
        ("Recorrido familiar por los senderos bajos", Decimal("20.00"), Decimal("10.00"), 3, False, familiar),
    ]
    objs = []
    for titulo, pa, pn, dur, finde, tipo in data:
        desc = "Experiencia guiada en el Volcán de San Miguel con personal certificado."
        objs.append(Tour(titulo=titulo, descripcion=desc, descripcion1=desc, descripcion2=desc,
            precio_adulto=pa, precio_nino=pn, duracion=dur, iva=True,
            incluye_tour="Guía, transporte e hidratación.", imagen="", tipo_tour=tipo,
            fecha_inicio=now, fecha_fin=fin, solo_finde=finde))
    Tour.objects.bulk_create(objs)
    tours = list(Tour.objects.all())
    for t in tours[:3]:
        Resena.objects.create(tour=t, estrellas=5, comentario="Excelente experiencia, muy recomendado.")


# ----------------- Servicios -----------------
def seed_servicios():
    from Servicios.models import TipoServicio, Servicios
    if Servicios.objects.exists():
        return
    aventura, _ = TipoServicio.objects.get_or_create(nombre="Turismo de aventura")
    hospedaje, _ = TipoServicio.objects.get_or_create(nombre="Hospedaje")
    data = [("Tours guiados", aventura), ("Zona de camping", hospedaje),
            ("Caminatas y senderismo", aventura), ("Alquiler de equipo", aventura),
            ("Parqueo", hospedaje)]
    objs = [Servicios(tipo=tp, nombre=n, descripcion="Servicio disponible en Volcano.", imagen="", url_servicio="#")
            for n, tp in data]
    Servicios.objects.bulk_create(objs)


# ----------------- Nosotros -----------------
def seed_nosotros():
    from Nosotros.models import Nosotros, Nosotros_Servicios, Nosotros_Oferta, Generalidades
    if not Nosotros.objects.exists():
        Nosotros.objects.bulk_create([Nosotros(titulo="Sobre Volcano", subtitulo="Turismo en el Volcán de San Miguel",
            descripcion="Empresa de turismo de aventura: tours, camping y caminatas.",
            imagen="", imagen_pequena_1="", imagen_pequena_2="", texto_boton="Conoce más", url_boton="#")])
    if not Nosotros_Servicios.objects.exists():
        Nosotros_Servicios.objects.bulk_create([
            Nosotros_Servicios(servicio_titulo="Tours al volcán", servicio_descripcion="Ascensos guiados.", servicio_icono=""),
            Nosotros_Servicios(servicio_titulo="Camping", servicio_descripcion="Zona equipada.", servicio_icono=""),
            Nosotros_Servicios(servicio_titulo="Caminatas", servicio_descripcion="Senderos guiados.", servicio_icono=""),
            Nosotros_Servicios(servicio_titulo="Alquiler de equipo", servicio_descripcion="Tiendas y más.", servicio_icono=""),
        ])
    if not Nosotros_Oferta.objects.exists():
        Nosotros_Oferta.objects.bulk_create([
            Nosotros_Oferta(titulo_oferta="Paquete Aventura", porcentaje_descuento="10", servicio_descuento="Camping + Tour",
                descripcion="Paquete completo de aventura.", detalle_1="Tour al cráter", detalle_2="Noche de camping",
                detalle_3="Alimentación", estado_oferta=True, oferta_imagen=""),
            Nosotros_Oferta(titulo_oferta="Combo Familiar", porcentaje_descuento="15", servicio_descuento="Senderismo",
                descripcion="Ideal para familias.", detalle_1="Guía", detalle_2="Hidratación",
                detalle_3="Seguro", estado_oferta=True, oferta_imagen=""),
        ])
    if not Generalidades.objects.exists():
        Generalidades.objects.create(terminos="Términos de uso.", condiciones="Condiciones de reserva.",
            politicas="Política de privacidad y cancelación.", mision="Promover el turismo responsable en el volcán.",
            vision="Ser la principal experiencia turística del oriente de El Salvador.")


# ----------------- Internet -----------------
def seed_internet():
    from Internet.models import Tipos, Accesos, Clientes
    if not Tipos.objects.exists():
        Tipos.objects.bulk_create([
            Tipos(nombre="Plan 1 hora", tiempo_conexion="1 hora", velocidad_mb="5", descripcion="Acceso por 1 hora",
                  precio=Decimal("1.0000"), imagen_tipo="", nombre_perfil="1h", nombre_servidor="hotspot"),
            Tipos(nombre="Plan 1 día", tiempo_conexion="24 horas", velocidad_mb="10", descripcion="Acceso por 1 día",
                  precio=Decimal("3.0000"), imagen_tipo="", nombre_perfil="1d", nombre_servidor="hotspot"),
            Tipos(nombre="Plan semanal", tiempo_conexion="7 días", velocidad_mb="10", descripcion="Acceso semanal",
                  precio=Decimal("5.0000"), imagen_tipo="", nombre_perfil="7d", nombre_servidor="hotspot"),
        ])
    if not Accesos.objects.exists():
        tipos = list(Tipos.objects.all())
        for i in range(1, 7):
            t = tipos[i % len(tipos)]
            Accesos.objects.create(usuario=f"wifi{i:03d}", password=f"pass{i:03d}", descripcion="Acceso WiFi",
                cant_usuarios=1, acceso_tipo=t, estado=True)
    if not Clientes.objects.exists():
        for n, a in [("Pedro", "García"), ("Lucía", "Martínez"), ("José", "Hernández")]:
            Clientes.objects.create(nombre=n, apellido=a, direccion="San Miguel", dui="00000000-0",
                email=f"{n.lower()}@example.com", telefono="+503 7000-0000")


# ----------------- TPV: Categorías, Proveedores, Productos, Clientes, Alquiler, Cajas -----------------
def seed_tpv():
    from TPV_.Productos.models import Categoria, Producto
    from TPV_.Proveedores.models import Proveedor
    from TPV_.Clientes.models import Cliente
    from TPV_.Alquileres.models import ArticuloAlquiler
    from TPV_.Cajas.models import Cajas
    from TPV_.Kardex.services import registrar_movimiento

    if not Proveedor.objects.exists():
        Proveedor.objects.create(nombre="Distribuidora La Cumbre", dui="0", nit=0,
            nombre_comercial="La Cumbre", direccion="San Miguel", telefono=22000000, email="ventas@lacumbre.sv")
        Proveedor.objects.create(nombre="Abarrotes del Oriente", dui="0", nit=0,
            nombre_comercial="Del Oriente", direccion="San Miguel", telefono=22000001, email="info@oriente.sv")

    cats = {}
    if not Categoria.objects.exists():
        for c in ["Bebidas", "Snacks", "Dulces", "Galletas", "Abarrotes"]:
            cats[c] = Categoria.objects.create(nombre=c)
    else:
        for c in Categoria.objects.all():
            cats[c.nombre] = c

    if not Producto.objects.exists():
        prov = Proveedor.objects.first()
        productos = [
            ("Agua 500ml", "Bebidas", "0.50", 40), ("Jugo de naranja 500ml", "Bebidas", "0.75", 30),
            ("Gaseosa lata", "Bebidas", "0.90", 36), ("Café caliente", "Bebidas", "1.00", 25),
            ("Papas fritas", "Snacks", "1.25", 20), ("Churros", "Snacks", "1.00", 18),
            ("Maní salado", "Snacks", "0.75", 24), ("Chocolate", "Dulces", "1.10", 30),
            ("Paleta helada", "Dulces", "0.35", 50), ("Chicle", "Dulces", "0.25", 60),
            ("Galletas saladas", "Galletas", "0.90", 28), ("Galletas dulces", "Galletas", "1.00", 28),
            ("Pan dulce", "Abarrotes", "0.60", 22), ("Atún en lata", "Abarrotes", "1.75", 15),
            ("Fósforos", "Abarrotes", "0.50", 40),
        ]
        for nombre, cat, precio, stock in productos:
            p = Producto.objects.create(nombre=nombre, categoria=cats.get(cat), proveedor=prov,
                precio_de_venta=Decimal(precio), precio_de_compra=Decimal(precio) * Decimal("0.7"),
                stock=0, stock_minimo=5, status="A", codigo_de_barras="", imagen="")
            registrar_movimiento(p, "entrada", stock, usuario=admin, motivo="Carga inicial")

    if not Cliente.objects.exists():
        for n, a, tel in [("Juan", "Pérez", "7111-1111"), ("Sofía", "Ramírez", "7222-2222"),
                          ("Miguel", "Castro", "7333-3333"), ("Elena", "Flores", "7444-4444"),
                          ("Roberto", "Díaz", "7555-5555")]:
            Cliente.objects.create(nombre=n, apellido=a, telefono=tel, pais="El Salvador", estado="ACTIVO")

    if not ArticuloAlquiler.objects.exists():
        arts = [
            ("Tienda de campaña 4 personas", "Tienda", 8, "15.00", "25.00"),
            ("Tienda de campaña 2 personas", "Tienda", 6, "10.00", "20.00"),
            ("Colchoneta inflable", "Colchoneta", 15, "5.00", "10.00"),
            ("Hamaca", "Hamaca", 12, "4.00", "8.00"),
            ("Sleeping bag", "Sleeping", 20, "6.00", "12.00"),
        ]
        for nombre, cat, total, tarifa, dep in arts:
            ArticuloAlquiler.objects.create(nombre=nombre, categoria=cat, cantidad_total=total,
                cantidad_disponible=total, tarifa=Decimal(tarifa), deposito_sugerido=Decimal(dep),
                activo=True, imagen="")

    if not Cajas.objects.exists():
        Cajas.objects.create(numero_caja="CAJA-01", nombre_caja="Caja principal", estado="abierto",
            efectivo_inicial=Decimal("50.00"), monto_total_efectivo=Decimal("50.00"), monto_ventas=Decimal("0.00"),
            monto_gastos_devoluciones=Decimal("0.00"), usuario_responsable=admin, fecha_hora_apertura=now)
        Cajas.objects.create(numero_caja="CAJA-02", nombre_caja="Caja secundaria", estado="cerrado",
            efectivo_inicial=Decimal("0.00"), monto_total_efectivo=Decimal("0.00"), usuario_responsable=admin,
            fecha_hora_apertura=now)


# ----------------- Ventas y Alquiler de ejemplo (movimientos) -----------------
def seed_movimientos():
    from django.db import transaction
    from TPV_.Productos.models import Producto
    from TPV_.Cajas.models import Cajas
    from TPV_.Clientes.models import Cliente
    from TPV_.Ventas.models import Ventas, DetalleVenta
    from TPV_.Alquileres.models import ArticuloAlquiler, Alquiler, AlquilerDetalle
    from TPV_.Kardex.services import registrar_movimiento
    from TPV_.Cajas.services import registrar_movimiento_caja
    from TPV_.utils import desglose_iva, q

    if Ventas.objects.exists():
        return
    caja = Cajas.objects.filter(estado="abierto").first()
    if not caja:
        return
    cliente = Cliente.objects.first()
    prods = list(Producto.objects.all()[:3])

    # Venta de ejemplo
    with transaction.atomic():
        items = [(prods[0], 2), (prods[1], 3)]
        total = sum((p.precio_de_venta * c for p, c in items), Decimal("0"))
        subtotal, iva = desglose_iva(total)
        v = Ventas.objects.create(caja=caja, cliente=cliente, usuario=admin, tipo_pago="efectivo",
            subtotal=subtotal, iva=iva, total=q(total), recibe_caja=q(total), cambio=Decimal("0.00"), estado="F")
        v.numero = f"VL-{v.pk:05d}"; v.save(update_fields=["numero"])
        for p, c in items:
            st, si = desglose_iva(p.precio_de_venta * c)
            DetalleVenta.objects.create(venta=v, producto=p, cantidad=c,
                precio_unitario=p.precio_de_venta, iva=si, subtotal=q(p.precio_de_venta * c))
            registrar_movimiento(p, "salida", -c, usuario=admin, referencia=v.numero)
        registrar_movimiento_caja(caja, admin, "venta", efectivo=q(total), venta=q(total), motivo=f"Venta {v.numero}")

    # Alquiler de ejemplo
    art = ArticuloAlquiler.objects.first()
    if art and not Alquiler.objects.exists():
        with transaction.atomic():
            art = ArticuloAlquiler.objects.select_for_update().get(pk=art.pk)
            cant = 2
            art.cantidad_disponible -= cant; art.save(update_fields=["cantidad_disponible"])
            a = Alquiler.objects.create(cliente=cliente, caja=caja, usuario=admin, estado="activo",
                tipo_pago="efectivo", deposito=art.deposito_sugerido, total_tarifa=q(art.tarifa * cant))
            a.numero = f"AL-{a.pk:05d}"; a.save(update_fields=["numero"])
            AlquilerDetalle.objects.create(alquiler=a, articulo=art, cantidad=cant, tarifa_unitaria=art.tarifa)
            registrar_movimiento_caja(caja, admin, "venta", efectivo=q(art.tarifa * cant),
                venta=q(art.tarifa * cant), motivo=f"Alquiler {a.numero}")


# ----------------- Contacto -----------------
def seed_contacto():
    from Contactanos.models import Mensaje_Contacto
    if not Mensaje_Contacto.objects.exists():
        Mensaje_Contacto.objects.bulk_create([
            Mensaje_Contacto(nombre="Visitante 1", asunto="Consulta de tours", email="v1@example.com", mensaje="¿Tienen tours este fin de semana?"),
            Mensaje_Contacto(nombre="Visitante 2", asunto="Camping", email="v2@example.com", mensaje="¿Cuánto cuesta acampar?"),
        ])


for label, fn in [
    ("Configuraciones", seed_config), ("Tours", seed_tours), ("Servicios", seed_servicios),
    ("Nosotros", seed_nosotros), ("Internet", seed_internet), ("TPV", seed_tpv),
    ("Ventas/Alquiler demo", seed_movimientos), ("Contacto", seed_contacto),
]:
    section(label, fn)

print("=== SEED DEV COMPLETO ===")
