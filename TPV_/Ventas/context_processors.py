from TPV_.Productos.models import Categoria


def categorias_context_processor(request):
    return {'categorias': Categoria.objects.all()}