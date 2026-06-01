from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.forms import *
from .forms import *
from django.db.models import Count, Q
from .models import *
from .models import PPESizeQuantity
from itertools import zip_longest
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
@login_required
def master_list(request):
    """list all ppe master"""
    ppe_list = PPEItem.objects.all()
    query = request.GET.get('search')

    if query:
        ppe_list = ppe_list.filter(
            Q(name__icontains=query) |
            Q(category__category_name__icontains=query)|
            Q(ppe_code__icontains=query)
        )

    context = {
        "ppe_list": ppe_list
    }

    paginator = Paginator(ppe_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'PPE/configuration/master_list.html',
        {
            'page_obj': page_obj
        }
    )
    

@login_required
def create_ppe(request):

    if request.method == 'POST':
        form = PPEItemForm(request.POST)

        if form.is_valid():
            ppe = form.save(commit=False)
            ppe.is_active = request.POST.get('is_active') == 'on'

            # Save PPE
            ppe.save()
            sizes = request.POST.getlist('size[]')
            for size in sizes:
                if size and size.strip():
                    PPESizeQuantity.objects.create(
                        ppe_item=ppe,
                        size=size.strip()
                    )
            messages.success(
                request,
                f'PPE "{ppe.name}" created successfully!'
            )
            return redirect('PPE:master_list')
        messages.error(request, "Please correct the errors below.")
    else:
        form = PPEItemForm()
    context = {
        'form': form,
        'categories': PPECategory.objects.filter(is_active=True),
        'ppe_code': PPEItem.generate_ppe_code(),  # FIXED (classmethod)
        'action': 'Create',
        'title': 'Create PPE Item'
    }
    return render(request, 'PPE/configuration/create_ppe.html', context)

@login_required
def ppe_detail(request, pk):
    ppe = get_object_or_404(PPEItem, pk=pk)

    size_quantities = PPESizeQuantity.objects.filter(ppe_item=ppe)

    context = {
        'ppe': ppe,
        'size_quantities': size_quantities,
    }

    return render(request, 'PPE/configuration/ppe_detail.html', context)
@login_required
def ppe_delete(request, pk):
    ppe = get_object_or_404(PPEItem, pk=pk)
    if request.method == "POST":
        ppe_name = ppe.name
        ppe.delete()
        messages.success(request, f'PPE Item "{ppe_name}" deleted successfully!')
        return redirect('PPE:master_list')
    return render(request, 'PPE/configuration/ppe_delete.html', {
        'ppe': ppe
    })
@login_required
def master_edit(request, pk):
    ppe = get_object_or_404(PPEItem, pk=pk)

    if request.method == 'POST':
        form = PPEItemForm(request.POST, instance=ppe)

        if form.is_valid():
            ppe = form.save()
            #delete existing size
            ppe.size_quantities.all().delete()

            # Save updated sizes
            sizes = request.POST.getlist('size[]')

            for size in sizes:
                if size.strip():
                    PPESizeQuantity.objects.create(
                        ppe_item=ppe,
                        size=size.strip()
                    )

            messages.success(request, "PPE updated successfully!")
            return redirect('PPE:master_list')

    return render(
        request,
        'PPE/configuration/create_ppe.html',
        {
            'ppe': ppe,
            'categories': PPECategory.objects.filter(is_active=True),
            'existing_sizes': ppe.size_quantities.all(),
            'action': 'Edit'
        }
    )