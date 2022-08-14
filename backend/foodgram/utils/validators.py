from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

min_value_validator = MinValueValidator(0, _('Значение должно быть больше 0'))
