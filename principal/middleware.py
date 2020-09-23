from django.utils.deprecation import MiddlewareMixin


class SetApplicationNameMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.current_app = view_func.__module__.split('.')[0]
