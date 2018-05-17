from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.utils import timezone
from .forms import PostForm, UserForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse 
from django.contrib.auth import logout, authenticate, login



# Create your views here.
def post_list(request):
	posts = Post.objects.filter(publish_date__lte=timezone.now()).order_by('publish_date')
	return render(request, 'blog/post_list.html',{'posts': posts})

def post_detail(request,pk):
	posts = get_object_or_404(Post, pk=pk)
	return render(request, 'blog/post_detail.html',{'post': posts})

@login_required
def post_new(request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			#post.publish_date = timezone.now()
			post.save()
			return redirect('post_detail', pk=post.pk)
	else:
		form = PostForm()
		return render(request, 'blog/post_edit.html',{'form': form})

@login_required
def post_edit(request,pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == "POST":
		form = PostForm(request.POST, instance=post)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			#post.publish_date = timezone.now()
			post.save()
			return redirect('post_detail',pk=pk)
	else:
		form = PostForm(instance=post)
		return render(request, 'blog/post_edit.html',{'form':form})

@login_required
def post_draft_list(request):
	posts = Post.objects.filter(publish_date__isnull=True).order_by('created_date')
	return render(request,'blog/post_draft_list.html',{'posts': posts})

@login_required
def post_publish(request,pk):
	post = get_object_or_404(Post, pk=pk)
	post.publish()
	return redirect('post_detail', pk=pk)

@login_required
def post_delete(request,pk):
	post = get_object_or_404(Post, pk=pk)
	post.delete()
	return redirect('post_list')

def register(request):
	form = UserForm()

	if request.method == 'POST':
		form = UserForm(request.POST)

		if form.is_valid():
			user = form.save()
			print ("Before hashing -->"+ user.password)
			user.set_password(user.password)
			print ("After Hashing -->" + user.password)
			user.save()
			return HttpResponseRedirect(reverse('post_list'))
		else:
			print (form.errors)

	return render(request, 'registration/register.html', {'form': form})

def my_login(request):
	error_msg = None
	if request.method == 'POST':
		username = request.POST.get('username')	
		password = request.POST.get('password')

		print("User name  --->"+username)
		print("password --->"+ password)
		user = authenticate(username=username, password=password)

		print(user)
		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('post_list'))
			else:
				error_msg = "Your Account is disabled"
		else:
			error_msg = "Your Username or Password is wrong"

	return render(request, 'registration/login.html', {'error_msg': error_msg})

