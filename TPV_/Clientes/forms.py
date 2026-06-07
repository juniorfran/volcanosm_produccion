from django import forms

from TPV_.Clientes.models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # Solo el nombre es obligatorio; el resto es opcional (cliente de mostrador).
        fields = (
            'nombre', 'apellido', 'telefono', 'email',
            'tipo_documento', 'numero_documento', 'pais', 'direccion', 'estado',
        )
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'tipo_documento': 'Tipo de documento',
            'numero_documento': 'Número de documento',
            'pais': 'País',
            'estado': 'Estado',
            'direccion': 'Dirección',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo "nombre" es obligatorio.
        for f in ('apellido', 'telefono', 'email', 'tipo_documento',
                  'numero_documento', 'pais', 'direccion', 'estado'):
            if f in self.fields:
                self.fields[f].required = False
        if not self.instance.pk:
            self.initial.setdefault('pais', 'El Salvador')
            self.initial.setdefault('estado', 'ACTIVO')

    def clean_estado(self):
        return self.cleaned_data.get('estado') or 'ACTIVO'
