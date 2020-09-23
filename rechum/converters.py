from datetime import datetime


class FourDigitsYearConverter:
    regex = '(19|20)[0-9]{2}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value


class TwoDigitsMonthConverter:
    regex = '0?[1-9]|1[0-2]'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%02d' % value


class TwoDigitsDayConverter:
    regex = '3[01]|[12][0-9]|0?[1-9]'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%02d' % value


class DateConverter:
    # yyyy-mm-dd
    regex = '((19|20)[0-9]{2})-(0?[1-9]|1[0-2])-(3[01]|[12][0-9]|0?[1-9])'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return datetime.strftime(value, '%Y-%m-%d')
