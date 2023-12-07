from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from .models import Hall, Video
from .forms import VideoForm, SearchForm
from django.forms import formset_factory
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404, JsonResponse
import urllib
import requests
from django.forms.utils import ErrorList
# Create your views here.

YOUTUBE_API_KEY = 'AIzaSyAMrY6sp7LbgDi5lIgy74T-e5SLevSG_PI'


def home(request):
    return render(request, 'halls/home.html')


def dashboard(request):
    return render(request, 'halls/dashboard.html')


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'
    # we can make the user login directly after signup

    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get(
            'username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view


class CreateHall(generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form)
        return redirect('home')


class DetailHall(generic.DetailView):
    model = Hall
    template_name = 'halls/detail_hall.html'


class UpdateHall(generic.UpdateView):
    model = Hall
    template_name = 'halls/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')


class DeleteHall(generic.DeleteView):
    model = Hall
    template_name = 'halls/delete_hall.html'
    success_url = reverse_lazy('dashboard')

# use cbv if ur using a particular base of  a model which is not too complicated
# like for an object if we want to create a view to create,update delete then use cbv
# for The model Video it might get a bit messy using only cbvs then we use function based views as well


def add_video(request, pk):
    # VideoFormset = formset_factory(VideoForm, extra=5)
    # form = VideoFormset()
    hall = Hall.objects.get(pk=pk)
    if not hall.user == request.user:
        raise Http404
    form = VideoForm()
    search_form = SearchForm()
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            video = Video()
            video.url = form.cleaned_data['url']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id = video_id[0]
                response = requests.get(
                    f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id[0] }&key={YOUTUBE_API_KEY}')
                json = response.json()
                title = json['items'][0]['snippet']['title']
                video.title = title
                video.save()
                return redirect('detail_hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be a YouTube URL')
    return render(request, 'halls/add_video.html', {'form': form, 'search_form': search_form, 'hall': hall})


def video_search(request):
    search_form = SearchForm(request.GET)
    print(search_form.errors)
    if search_form.is_valid():
        return JsonResponse({'hello': search_form.cleaned_data['search_term']})
    return JsonResponse({'hello': 'error'})
