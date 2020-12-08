from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
	ListView, 
	DetailView,
	CreateView,
	UpdateView,
	DeleteView
)
from .models import Post
from .forms import CreateFileForm
import os


class node():
    def __init__(self,name,stat,path):
        self.name = name
        self.stat = stat
        self.child = []
        self.path= path
    def add_child(self,child_node):
        self.child.append(child_node)
        


def builder(top):
    curr = list(os.popen('ls'))

    for i in range(len(curr)):
        curr[i]= curr[i].strip()
        dir_check = os.path.isdir(curr[i])
        if(dir_check):
            new_dir=node(curr[i],'dir',top.path+"/"+curr[i])
            os.chdir(curr[i])
            builder(new_dir)
            os.chdir('..')
            top.add_child(new_dir)
        else:
            new_file=node(curr[i],'file',top.path+"/"+curr[i])
            top.add_child(new_file)









@login_required
def home(request):
	top = node('CodeFiles'+"/"+str(request.user.id),'dir','CodeFiles')
	os.chdir('CodeFiles'+"/"+str(request.user.id))
	builder(top)
	os.chdir('..')
	os.chdir('..')

	contents = [top]
	
	return render(request, 'blog/home.html', {'contents':contents})


class PostListView(ListView):
	model = Post
	template_name = 'blog/home.html'
	context_object_name = 'posts'
	ordering = ['-date_posted']


class PostDetailView(DetailView):
	model = Post

def detail(request):
	return render(request)	

@login_required
def create(request,folderpath):
	if request.method == 'POST':
		form = CreateFileForm(request.POST)
		
		if form.is_valid():
			form.save()

			title = form.cleaned_data.get('title')
			os.popen('touch %s/%s',(folderpath,title))
			return redirect('blog-home')
		
	else:
		form = CreateFileForm()
	
	return render(request, 'blog/create.html', {'form': form})



@login_required
def folderview(request,folderpath):
	print(folderpath)
	if request.method == 'POST':
		button = request.POST.get('pressed',False)
		if(button == "Create File"):
			return redirect("/create/"+folderpath+"!")
		elif( button == "Create Folder"):
			return redirect("/create/"+folderpath+"@")
		elif( button == "Delete Folder"):
			return redirect("/create/"+folderpath+"#")
		
			
		

	return render(request,'blog/folderview.html')
@login_required
def create_file_in_folder(request,folderpath):
	option = folderpath[len(folderpath)-1]
	if(option == '#'):
		folder_path= folderpath[:len(folderpath)-1]
		print(folder_path)
		os.popen('rm -rf %s' %folder_path)
		return redirect('blog-home')
	if request.method =='POST':
		
		if(option =='!'):
			filename = request.POST.get('filename',False)
			os.popen('touch %s/%s' %(folderpath[:len(folderpath)-1],filename))
			prev_url = '/folderview/'+folderpath[:len(folderpath)-1]
			return redirect('blog-home')
		elif(option =='@'):
			foldername= folderpath[:len(folderpath)-1]+"/"+request.POST.get('filename',False)
			os.popen('mkdir %s' %foldername)
			return redirect('blog-home')
	

			
	return render(request,'blog/create_file_in_folder.html',{"option":option})
	


class PostCreateView(LoginRequiredMixin, CreateView):
	model = Post
	fields = ['title']

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ['title']

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post
	success_url = '/'

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			os.popen(f'rm CodeFiles/{self.request.user.id}/{post.title}')
			return True
		return False



def about(request):
	return render(request, 'blog/about.html',{'title': 'About'})
