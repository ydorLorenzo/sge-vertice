from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db import IntegrityError


def login_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        acceso = authenticate(username=username, password=password)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                else:
                    return redirect('home_principal')
            else:
                context = {'info': "Usuario desactivado."}
                return render(request, 'login.html', context)
        else:
            context = {'info': "Usuario / Contraseña incorrecta"}
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html')


class SgeTemplateView(PermissionRequiredMixin, TemplateView):
    raise_exception = True


class SgeListView(PermissionRequiredMixin, ListView):
    raise_exception = True
    # allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs.update(_extra_context(self))
        if 'create_url' not in kwargs:
            kwargs.update({
                "create_url": reverse_lazy(self.model._meta.model_name + '_create'),
            })
        return super().get_context_data(object_list=object_list, **kwargs)


class SgeDetailView(PermissionRequiredMixin, DetailView):
    raise_exception = True

    def get_context_data(self, **kwargs):
        kwargs.update(_extra_context(self))
        return super().get_context_data(**kwargs)


class SgeCreateView(PermissionRequiredMixin, CreateView):
    raise_exception = True

    def get_context_data(self, **kwargs):
        kwargs.update(_extra_context(self))
        if 'list_url' not in kwargs:
            kwargs['list_url'] = reverse_lazy(self.model._meta.model_name + '_list')
        if 'create_url' not in kwargs:
            kwargs['create_url'] = reverse_lazy(self.model._meta.model_name + '_create')
        kwargs['update_url_name'] = self.model._meta.model_name + '_update'
        return super().get_context_data(**kwargs)


class SgeUpdateView(PermissionRequiredMixin, UpdateView):
    raise_exception = True

    def get_context_data(self, **kwargs):
        kwargs.update(_extra_context(self))
        if 'list_url' not in kwargs:
            kwargs["list_url"] = reverse_lazy(self.model._meta.model_name + '_list')
        if 'create_url' not in kwargs:
            kwargs["create_url"] = reverse_lazy(self.model._meta.model_name + '_create')
        kwargs["update_url_name"] = self.model._meta.model_name + '_update'
        return super().get_context_data(**kwargs)


class SgeDeleteView(PermissionRequiredMixin, DeleteView):
    raise_exception = True
    template_name = 'layouts/crud/delete.html'

    def get_context_data(self, **kwargs):
        kwargs.update(_extra_context(self))
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()
        except IntegrityError:
            return HttpResponseRedirect(
                self.object.get_list_url(args=['error_'+str(self.object.id)])
            )
        return HttpResponseRedirect(success_url)


def _extra_context(instance):
    return {
        "model_name": instance.model._meta.model_name,
        "verbose_name": instance.model._meta.verbose_name,
        "verbose_name_plural": instance.model._meta.verbose_name_plural,
        "base_module": f"layouts/_base_{instance.request.current_app}.html"
    }
