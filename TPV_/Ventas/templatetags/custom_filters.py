from django import template

register = template.Library()

@register.filter(name='get_by_id')
def get_by_id(queryset, id):
    try:
        return queryset.get(id=id)
    except queryset.model.DoesNotExist:
        return None
    
@register.filter
def get_value(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)