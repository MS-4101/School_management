from django import template

register = template.Library()

@register.filter
def get_range(value):
    return range(value)

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def percentage(value, total):
    try:
        return (value * 100) / total
    except (ValueError, ZeroDivisionError):
        return 0
