from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, ZeroDivisionError):
        return 0
    
@register.filter
def subtract(value, arg):
    """Subtracts the arg from the value"""
    return value - arg