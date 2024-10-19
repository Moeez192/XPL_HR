# your_app/templatetags/custom_tags.py
from django import template

register = template.Library()

@register.simple_tag
def custom_input(input_type, css_class, id_attr, placeholder, required=False):
    required_attr = 'required' if required else ''
    return f'<input type="{input_type}" class="{css_class}" id="{id_attr}" placeholder="{placeholder}" {required_attr}>'
