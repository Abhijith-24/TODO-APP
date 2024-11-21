from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm

# View for signup
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        re_password = request.POST['password2']
        
        # Check if passwords match
        if password != re_password:
            messages.error(request, "Passwords do not match.")
        else:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please try again with a different username.")
            else:
                # Create new user
                try:
                    user = User.objects.create_user(username=username, password=password)
                    messages.success(request, "Account created successfully. Please log in.")
                    return redirect('login')  # Redirect to login after successful signup
                except Exception as e:
                    messages.error(request, "Error: {e}")
    
    return render(request, 'accounts/signup.html')

# View for login
def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'accounts/login.html')

# view for homepage
def home(request):
    tasks = Task.objects.filter(user=request.user)  # Filter tasks by the logged-in user
    return render(request, 'accounts/home.html', {'tasks': tasks})

# View for logout
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  # Redirect to login page after logout

    
# List all tasks
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'accounts/task_list.html', {'tasks': tasks})

# Add a new task
@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # Save the task but associate it with the logged-in user
            task = form.save(commit=False)
            task.user = request.user  # Associate the task with the logged-in user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'accounts/add_task.html', {'form': form})

# Edit an existing task
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'accounts/edit_task.html', {'form': form, 'task': task})

# Delete a task (with confirmation)
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'accounts/delete_task.html', {'task': task})
