from django import template

register = template.Library()


@register.filter(name='read_perm')
def read_perm(app, model):
    return f"{app}.read_{model}"


@register.filter(name='change_perm')
def change_perm(app, model):
    return f"{app}.change_{model}"


@register.filter(name='add_perm')
def add_perm(app, model):
    return f"{app}.add_{model}"


@register.filter(name='delete_perm')
def delete_perm(app, model):
    return f"{app}.delete_{model}"


@register.filter(name='export_perm')
def export_perm(app, model):
    return f"{app}.export_{model}"


@register.filter(name='generate_perm')
def generate_perm(app, model):
    return f"{app}.generate_{model}"


@register.filter(name='has_module_perm')
def has_module_perm(user, model):
    return user.has_module_perms(model)
