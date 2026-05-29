from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.forms import *
from .forms import *
from django.db.models import Count, Q
from .models import *
from django.core.paginator import EmptyPage, Paginator


# Create your views here.

@login_required
def category_create(request):
    """Create new PPE Category"""
    
    if request.method == 'POST':
        form = PPECategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            messages.success(request, f'Category "{category.category_name}" created successfully!')
            return redirect('PPE:category_list')
    else:
        form = PPECategoryForm()
    
    context = {
        'form': form,
        'action': 'Create',
        'title': 'Create New Category'
    }
    return render(request, 'PPE/configuration/category_form.html', context)


@login_required
def category_edit(request, pk):
    """Edit existing category"""
    
    category = get_object_or_404(PPECategory, pk=pk)
    
    if request.method == 'POST':
        form = PPECategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.category_name}" updated successfully!')
            return redirect('PPE:category_list')
    else:
        form = PPECategoryForm(instance=category)
    
    context = {
        'form': form,
        'action': 'Edit',
        'title': f'Edit Category: {category.category_name}',
        'category': category
    }
    return render(request, 'PPE/configuration/category_form.html', context)

@login_required
def category_list(request):
    """List all Categories List"""
    
    categories = PPECategory.objects.order_by('category_name')
    
    # Filter
    search = request.GET.get('search')
    if search:
        categories = categories.filter(
            Q(category_name__icontains=search) |
            Q(category_code__icontains=search) |
            Q(description__icontains=search)
            
        )
    
    # Pagination
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search
    }
    return render(request, 'PPE/configuration/category_list.html', context)

@login_required
def category_delete(request, pk):
    """Permanently delete category"""
    category = get_object_or_404(PPECategory, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{category.category_name}" deleted successfully!')
        return redirect('PPE:category_list')
    
    context = {
        'category': category
    }
    return render(request, 'PPE/configuration/category_confirm_delete.html', context)