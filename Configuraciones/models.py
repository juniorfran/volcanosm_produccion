from django.db import models

# Create your models here.

class General_Description(models.Model):
    """
    This model represents the general description of a product. It is used to store information that applies to
    """
    titulo_largo = models.CharField( max_length=50)
    titulo_corto = models.CharField(max_length=30)
    medio_titulo = models.CharField(max_length=30)
    descripcion_larga = models.TextField(max_length=500)
    descripcion_corta = models.CharField(max_length=75)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = 'fecha_creacion'
        
    #funcion str
    def __str__(self):
        return self.titulo_largo
    

class Barra_Principal (models.Model):
    email_contacto = models.CharField(max_length=100)
    numero_contacto = models.CharField(max_length=50)
    url_facebook = models.CharField(max_length=100)
    url_twitter = models.CharField(max_length=100)
    url_linkedin = models.CharField(max_length=100)
    url_instagram = models.CharField(max_length=100)
    url_youtube = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = 'fecha_creacion'
        
    #la funcion str
    def __str__(self):
        return self.email_contacto + " - " + self.numero_contacto
    
def upload_to_carrusel_inicio(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'configuraciones/carrusel_inicio/{filename}'

class CarruselInicio(models.Model):
    #carrouser imagen
    titulo = models.CharField(max_length=100)
    contenido = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to=upload_to_carrusel_inicio, height_field=None, width_field=None, max_length=None)
    url_boton = models.CharField(max_length=100)
    texto_boton = models.CharField(max_length=50)
    
    #la funcion str
    def __str__(self):
        return self.titulo

def upload_to_services_bar(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'configuraciones/services_bar/{filename}'

class Services_Bar(models.Model):
    #barra de servicios
    services_visible = models.BooleanField()
    services_ico = models.ImageField( upload_to=upload_to_services_bar, height_field=None, width_field=None, max_length=None)
    services_ico_tag = models.CharField(max_length=150, null=True)
    services_name = models.CharField(max_length=50)
    services_description = models.CharField(max_length=250)
    
    #funcion str
    def __str__(self):
        return self.services_name

def upload_to_team_bar(instance, filename):
    # La función toma la instancia del modelo y el nombre del archivo y construye la ruta de almacenamiento
    return f'configuraciones/team_bar/{filename}'
    
class Team_bar(models.Model):
    #barra de equipos
    team_image = models.ImageField(upload_to=upload_to_team_bar, blank=False, null=False)
    team_nombre = models.CharField(max_length=40)
    team_job =  models.CharField(max_length=130)
    # email_contacto = models.CharField(max_length=100)
    # numero_contacto = models.CharField(max_length=50)
    url_facebook = models.CharField(max_length=100)
    url_twitter = models.CharField(max_length=100)
    url_linkedin = models.CharField(max_length=100)
    url_instagram = models.CharField(max_length=100)
    # url_youtube = models.CharField(max_length=100)
    #funcion str
    def __str__(self):
        return self.team_nombre+"-"+self.team_job
    #Se agrega un metodo a la clase Team_bar para que se
    #pongan las imagenes en orden inverso
    @property
    def is_last(self):
        """Return True if the team member is last."""
        return not Team_bar.objects.filter(id__gt=self.id).exists
    
    
#contac information
class Contacts(models.Model):
    contact_email = models.EmailField("Correo electronico", max_length=254, help_text="Ingrese su dirección de correo electrónico")
    contact_phone = models.CharField(max_length=50)
    addres = models.CharField(max_length=250)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = 'fecha_creacion'
    
    #funcion str
    def __str__(self):
        return self.contact_email
    
#urls de Secciones Principales 
class Urls_info(models.Model):
    title = models.CharField(max_length=50)
    url = models.CharField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #funcion str
    def __str__(self):
        return self.title

#urls de informacion de interes 
class Urls_interes(models.Model):
    title = models.CharField(max_length=50)
    url = models.URLField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    #funcion str
    def __str__(self):
        return self.title
    
    
    

    


