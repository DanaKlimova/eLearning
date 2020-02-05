from django.template.defaulttags import register


@register.filter
def get_list_item(list, index):
    return list[index]