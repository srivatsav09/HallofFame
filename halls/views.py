from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from .models import Hall
from django.contrib.auth.forms import UserCreationForm
# Create your views here.


def home(request):
    return render(request, 'halls/home.html')


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'


class CreateHall(generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('home')

# use cbv if ur using a particular base of  a model which is not too complicated
# like for an object if we want to create a view to create,update delete then use cbv
# for The model Video it might get a bit messy using only cbvs then we use function based views as well
