from django.utils import timezone
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import TipoTour, Tour, ImagenTour, Resena, Reserva
import csv
from reportlab.pdfgen import canvas
from reportlab.lib import colors

@admin.register(TipoTour)
class TipoTourAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descripcion', 'precio_adulto', 'precio_nino', 'duracion', 'iva', 'tipo_tour', 'fecha_inicio', 'fecha_fin', 'mostrar_imagen_azure')
    search_fields = ('titulo', 'descripcion', 'tipo_tour__nombre',)
    
    def mostrar_imagen_azure(self, obj):
        if obj.url_azure:
            return format_html('<img src="{}" width="100" />', obj.url_azure)
        else:
            return 'No disponible'

    mostrar_imagen_azure.short_description = 'Imagen Azure'

@admin.register(ImagenTour)
class ImagenTourAdmin(admin.ModelAdmin):
    list_display = ('tour','imagen1')

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('tour', 'estrellas', 'comentario',)
    search_fields = ('tour__titulo', 'comentario',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo_reserva', 'nombre', 'dui', 'telefono', 'correo_electronico','tour', 'direccion', 'cantidad_adultos', 'cantidad_ninos', 'fecha_reserva', 'total_pagar',)
    search_fields = ('tour__titulo', 'codigo_reserva', 'nombre', 'telefono', 'dui', 'correo_electronico',)
    list_filter = ('fecha_reserva',)

    actions = ['exportar_a_excel', 'generar_reporte_pdf']

    def exportar_a_excel(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reservas.csv"'

        writer = csv.writer(response)
        writer.writerow(['Código de Reserva', 'Nombre', 'DUI', 'Teléfono', 'Correo Electrónico', 'Tour', 'Dirección', 'Cantidad de Adultos', 'Cantidad de Niños', 'Fecha de Reserva', 'Total a Pagar'])

        for reserva in queryset:
            writer.writerow([reserva.codigo_reserva, reserva.nombre, reserva.dui, reserva.telefono, reserva.correo_electronico, reserva.tour, reserva.direccion, reserva.cantidad_adultos, reserva.cantidad_ninos, reserva.fecha_reserva, reserva.total_pagar])

        return response

    exportar_a_excel.short_description = "Exportar a Excel"

    def generar_reporte_pdf(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reservas.pdf"'

        p = canvas.Canvas(response)
        p.setTitle("Reporte de Reservas")  # Título del PDF

        # Encabezado de la primera página
        p.setFont("Helvetica-Bold", 16)  # Fuente en negrita, tamaño 16
        p.drawString(100, 800, "Reporte de Reservas")  # Título del reporte
        p.setFont("Helvetica", 12)  # Restauramos la fuente a la normalidad
        p.drawString(100, 780, f"Fecha de Generación: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")  # Fecha de generación del reporte
        p.drawString(100, 760, f"Reservas Seleccionadas: {len(queryset)}")  # Cantidad de reservas seleccionadas
        p.setLineWidth(2)  # Grosor de las líneas divisoras
        p.line(100, 750, 500, 750)  # Línea divisora entre el encabezado y el contenido

        # Contenido de las reservas
        y = 700
        line_height = 20  # Altura de línea
        max_y = 100  # Altura máxima permitida antes de iniciar una nueva página

        for reserva in queryset:
            if y <= max_y:
                p.showPage()  # Agregar una nueva página
                p.setFont("Helvetica-Bold", 16)  # Restaurar la fuente del encabezado
                p.drawString(100, 800, "Reporte de Reservas")  # Restaurar el título del reporte
                p.setFont("Helvetica", 12)  # Restaurar la fuente a la normalidad
                p.drawString(100, 780, f"Fecha de Generación: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")  # Restaurar la fecha de generación del reporte
                p.drawString(100, 760, f"Reservas Seleccionadas: {len(queryset)}")  # Restaurar la cantidad de reservas seleccionadas
                p.setLineWidth(2)  # Restaurar el grosor de las líneas divisoras
                p.line(100, 750, 500, 750)  # Restaurar la línea divisora entre el encabezado y el contenido
                y = 700  # Restaurar la posición vertical

            p.drawString(100, y, f"Código de Reserva: {reserva.codigo_reserva}")
            p.drawString(100, y - line_height, f"Nombre: {reserva.nombre}")
            p.drawString(100, y - 2 * line_height, f"DUI: {reserva.dui}")
            p.drawString(100, y - 3 * line_height, f"Teléfono: {reserva.telefono}")
            p.drawString(100, y - 4 * line_height, f"Correo Electrónico: {reserva.correo_electronico}")
            p.drawString(100, y - 5 * line_height, f"Tour: {reserva.tour}")
            p.drawString(100, y - 6 * line_height, f"Dirección: {reserva.direccion}")
            p.drawString(100, y - 7 * line_height, f"Cantidad de Adultos: {reserva.cantidad_adultos}")
            p.drawString(100, y - 8 * line_height, f"Cantidad de Niños: {reserva.cantidad_ninos}")
            p.drawString(100, y - 9 * line_height, f"Fecha de Reserva: {reserva.fecha_reserva}")
            p.drawString(100, y - 10 * line_height, f"Total a Pagar: {reserva.total_pagar}")

            y -= 12 * line_height

        p.showPage()  # Asegúrate de mostrar la última página
        p.save()

        return response

    generar_reporte_pdf.short_description = "Generar Reporte en PDF"