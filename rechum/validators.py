import datetime

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

person_name_validator = RegexValidator(
    regex='^[A-Z]{1}[A-Za-záéíóúñ .]+$',
    message='Nombre inválido. Debe comenzar con mayúscula y no puede contener números ni caracteres especiales.'
)

general_name_validator = RegexValidator(
    regex='^[A-Z]{1}[A-Za-z0-9áéíóúñ .,#\'\"()]+$',
    message=_('Nombre inválido. Debe comenzar con mayúscula, y no presentar caracteres especiales.')
)

positive_number_validator = MinValueValidator(0, 'Valor inválido. El valor debe ser mayor o igual que 0.')


class IDValidator(RegexValidator):
    regex = '^[0-9]{2}(0[1-9]|1[0-2])(3[01]|[12][0-9]|0?[1-9])[0-9]{5}$'
    message = _('Número de carnet de identidad inválido (%(value)s).')

    def __call__(self, value):
        try:
            super().__call__(value)
        except ValidationError as err:
            raise ValidationError(err.message, code=err.code, params={'value': value})


class MinAgeValidator(MinValueValidator):
    message = _(
        'Cerciórese que la fecha sea la correcta. Edad por debajo de %(limit_value)s años (%(show_value)s años).')
    code = 'min_age'

    def clean(self, born):
        today = datetime.date.today()
        try:
            birthday = born.replace(year=today.year)
        except ValueError:
            birthday = born.replace(year=today.year, month=born.month + 1, day=1)
        if birthday > today:
            return today.year - born.year - 1
        return today.year - born.year


class MaxAgeValidator(MinAgeValidator):
    message = _(
        'Cerciórese que la fecha sea la correcta. Edad por encima de %(limit_value)s años (%(show_value)s años).')
    code = 'max_age'

    def compare(self, a, b):
        return a > b


class MinAgeIDValidator(MinAgeValidator):
    message = _(
        'Compruebe el número de carnet. La edad del trabajador es menor de %(limit_value)s años (%(show_value)s años).')
    code = 'min_age_id'

    def clean(self, x):
        born_date = datetime.datetime.strptime(x[:6], '%y%m%d').date()
        if born_date.year > datetime.date.today().year:
            born_date.replace(year=born_date.year - 100)
        return super().clean(born_date)


class MaxAgeIDValidator(MinAgeIDValidator):
    message = _(
        'Compruebe el número de carnet. La edad del trabajador es mayor de %(limit_value)s años (%(show_value)s años).')
    code = 'max_age_id'

    def compare(self, a, b):
        return a > b

