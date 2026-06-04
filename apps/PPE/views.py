from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from apps.accounts.models import User
from django.db.models import Count, Q
from .models import PPESizeQuantity
from itertools import zip_longest
from .models import *
from .forms import *
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Sum
from datetime import date


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
@login_required
def stock_list(request):
    stocks = PPEStockTransaction.objects.select_related(
        'ppe_item',
        'ppe_item__category'
    ).order_by('-created_at')
    
    return render(request, 'ppe/configuration/stock_list.html', {
        'stocks': stocks
    })

@login_required
def stock_create(request):
    form = PPEStockTransactionForm(request.POST or None)
    selected_item = None
    sizes = []
    category = ""
    ppe_item_id = request.GET.get('ppe_item')
    if ppe_item_id:
        try:
            selected_item = PPEItem.objects.get(id=ppe_item_id)
            sizes = PPESizeQuantity.objects.filter(
                ppe_item=selected_item
            )
            category = selected_item.category.category_name
        except PPEItem.DoesNotExist:
            selected_item = None
    if request.method == "POST":
        ppe_item_id = request.POST.get('ppe_item')
        transaction_type = request.POST.get('transaction_type')
        unit = request.POST.get('unit')
        transaction_date = request.POST.get('transaction_date')
        reference_number = request.POST.get('reference_number')
        remarks = request.POST.get('remarks')
        size_ids = request.POST.getlist('size_id[]')
        qtys = request.POST.getlist('qty[]')
        if not ppe_item_id:
            messages.error(
                request,
                "Please select PPE Item."
            )
            return redirect('PPE:stock_create')
        ppe_item = PPEItem.objects.get(id=ppe_item_id)
        size_quantities = {}
        total = 0
        for size_id, qty in zip(size_ids, qtys):
            try:
                qty = int(qty or 0)
            except ValueError:
                qty = 0
            if qty > 0:
                size_obj = PPESizeQuantity.objects.get(
                    id=size_id
                )
                # ADD STOCK TO SIZE TABLE
                size_obj.available_quantity += qty
                size_obj.save()
                size_quantities[size_obj.size] = qty
                total += qty
        if total <= 0:
            return render(
                request,
                'ppe/configuration/stock_form.html',
                {
                    'form': form,
                    'selected_item': selected_item,
                    'sizes': sizes,
                    'category': category,
                    'today': timezone.now().date(),
                    'action': 'Create',
                    'error': 'Please enter quantity.'
                }
            )

        PPEStockTransaction.objects.create(
            ppe_item=ppe_item,
            size_quantities=size_quantities,
            quantity=total,
            total=total,
            transaction_type=transaction_type,
            unit=unit,
            transaction_date=transaction_date,
            reference_number=reference_number,
            remarks=remarks,
            created_by=request.user,
            is_active=True
        )

        messages.success(
            request,
            "Stock saved successfully."
        )

        return redirect('PPE:stock_list')

    return render(
        request,
        'ppe/configuration/stock_form.html',
        {
            'form': form,
            'selected_item': selected_item,
            'sizes': sizes,
            'category': category,
            'today': timezone.now().date(),
            'action': 'Create'
        }
    )
@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(PPEStockTransaction, pk=pk)
    selected_item = stock.ppe_item
    sizes = PPESizeQuantity.objects.filter(ppe_item=selected_item)
    category = selected_item.category.category_name
    if request.method == "POST":
        ppe_item_id = request.POST.get('ppe_item')
        transaction_type = request.POST.get('transaction_type')
        unit = request.POST.get('unit')
        transaction_date = request.POST.get('transaction_date')
        reference_number = request.POST.get('reference_number')
        remarks = request.POST.get('remarks')
        is_active = request.POST.get('is_active') == 'on'
        size_ids = request.POST.getlist('size_id[]')
        qtys = request.POST.getlist('qty[]')
        selected_item = PPEItem.objects.get(id=ppe_item_id)
        size_map = {
            str(s.id): s.size
            for s in PPESizeQuantity.objects.filter(id__in=size_ids)
        }
        size_quantities = {}
        total = 0
        for size_id, qty in zip(size_ids, qtys):
            try:
                quantity = int(qty or 0)
            except ValueError:
                quantity = 0

            if quantity > 0:
                size_name = size_map.get(str(size_id))
                if size_name:
                    size_quantities[size_name] = quantity
                    total += quantity
        if total <= 0:
            messages.error(request, "Quantity required")
            return render(request, 'ppe/configuration/stock_form.html', {
                'form': PPEStockTransactionForm(instance=stock),
                'stock': stock,
                'selected_item': selected_item,
                'sizes': sizes,
                'category': category,
                'action': 'Edit'
            })
        stock.ppe_item = selected_item
        stock.transaction_type = transaction_type
        stock.unit = unit
        stock.transaction_date = transaction_date
        stock.reference_number = reference_number
        stock.remarks = remarks
        stock.is_active = is_active
        stock.size_quantities = size_quantities
        stock.total = total
        stock.quantity = total
        stock.updated_by = request.user
        stock.save()
        return redirect('PPE:stock_list')
    saved_quantities = stock.size_quantities or {}
    for s in sizes:
        s.stock_quantity = saved_quantities.get(s.size, 0)
    return render(request, 'ppe/configuration/stock_form.html', {
        'form': PPEStockTransactionForm(instance=stock),
        'stock': stock,
        'selected_item': selected_item,
        'sizes': sizes,
        'category': category,
        'transaction_date': stock.transaction_date,
        'action': 'Edit'
    })
@login_required
def stock_detail(request, pk):
    stock = get_object_or_404(PPEStockTransaction, pk=pk)
    saved_quantities = stock.size_quantities or {}
    return render(request, 'ppe/configuration/stock_detail.html', {
        'stock': stock,
        'saved_quantities': saved_quantities
    })
@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(PPEStockTransaction, pk=pk)
    if request.method == "POST":
        stock.delete()
        messages.success(request, "Stock deleted successfully")
        return redirect('PPE:stock_list')
    return render(request, 'ppe/configuration/stock_delete.html', {
        'stock': stock
    })

@login_required
def IssueManagement_list(request):
    search = request.GET.get('search', '')
    issues = PPEIssueManagement.objects.select_related(
        'ppe_item',
        'employee',
        'department',
        'created_by'
    ).order_by('-id')
    if search:
        issues = issues.filter(
            ppe_item__name__icontains=search
        )
    paginator = Paginator(issues, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    return render(
        request,
        'ppe/Management/IssueManagement_list.html',
        context
    )

@login_required
def IssueManagement_create(request):
    selected_item = None
    available_quantity = 0
    sizes = []
    ppe_item_id = request.GET.get('ppe_item')
    employees = User.objects.filter(
        is_active=True
    ).select_related(
        'department'
    )
    if ppe_item_id:
        selected_item = PPEItem.objects.get(
            id=ppe_item_id
        )
        available_quantity = (
            PPEStockTransaction.objects.filter(
                ppe_item=selected_item
            ).aggregate(
                total_stock=Sum('total')
            )['total_stock'] or 0
        )
        sizes = PPESizeQuantity.objects.filter(
            ppe_item=selected_item
        )
    if request.method == 'POST':
        print(request.POST)
        form = PPEIssueManagementForm(
            request.POST
        )
        if form.is_valid():
            issue = form.save(
                commit=False
            )
            stock_qty = (
                PPEStockTransaction.objects.filter(
                    ppe_item=issue.ppe_item
                ).aggregate(
                    total_stock=Sum('total')
                )['total_stock'] or 0
            )
            issue.available_quantity = stock_qty
            if issue.quantity_issue > stock_qty:
                messages.error(
                    request,
                    f"Only {stock_qty} quantity available."
                )
            else:
                if issue.employee:
                    issue.department = (
                        issue.employee.department
                    )
                issue.created_by = request.user
                issue.save()
                messages.success(
                    request,
                    "PPE Issued Successfully."
                )
                return redirect(
                    'PPE:IssueManagement_list'
                )
        else:
            print(form.errors)
    else:
        form = PPEIssueManagementForm()
    context = {
        'form': form,
        'selected_item': selected_item,
        'available_quantity': available_quantity,
        'sizes': sizes,
        'employees': employees,

    }
    return render(
        request,
        'ppe/Management/IssueManagement_create.html',
        context
    )
@login_required
def get_employee_department(request):
    employee_id = request.GET.get(
        'employee_id'
    )
    try:
        employee = User.objects.select_related(
            'department'
        ).get(
            id=employee_id
        )
        return JsonResponse({
            'department':
            employee.department.name
            if employee.department
            else ''
        })
    except User.DoesNotExist:
        return JsonResponse({
            'department': ''
        })