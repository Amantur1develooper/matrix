from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return None

@register.filter
def calculate_discount_percent(original_price, discount_price):
    try:
        original = float(original_price)
        discount = float(discount_price)
        return int(100 - (discount / original * 100))
    except (ValueError, ZeroDivisionError, TypeError):
        return 0