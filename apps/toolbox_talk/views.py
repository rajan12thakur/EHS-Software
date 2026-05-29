from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .forms import ToolboxTalkCategoryForm
from .models import ToolboxTalkCategory


def toolbox_category_create(request):

    """
    Create Toolbox Talk Category

    Developed by Rajan
    """

    # FORM SUBMIT
    if request.method == 'POST':

        form = ToolboxTalkCategoryForm(
            request.POST
        )

        # VALIDATION
        if form.is_valid():

            category = form.save(commit=False)

            category.created_by = request.user

            category.save()

            messages.success(
                request,
                'Category created successfully.'
            )

            return redirect(
                'toolbox_talk:toolbox_category_list'
            )

    # PAGE LOAD
    else:

        form = ToolboxTalkCategoryForm()

    context = {
        'form': form
    }

    return render(
        request,
        'toolbox_talk/create_category.html',
        context
    )


def toolbox_category_list(request):

    """
    Toolbox Talk Category List

    Developed by Rajan
    """

    categories = ToolboxTalkCategory.objects.all().order_by('-id')

    # SEARCH
    search = request.GET.get('search')

    if search:

        categories = categories.filter(
            Q(category_name__icontains=search) |
            Q(short_code__icontains=search)
        )

    # STATUS FILTER
    status = request.GET.get('status')

    if status == 'active':

        categories = categories.filter(
            status=True
        )

    elif status == 'inactive':

        categories = categories.filter(
            status=False
        )

    # PAGINATION
    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'page_obj': page_obj,
        'search': search,
        'status': status
    }

    return render(
        request,
        'toolbox_talk/category_list.html',
        context
    )


def toolbox_category_update(request, pk):

    """
    Update Toolbox Talk Category

    Developed by Rajan
    """

    category = get_object_or_404(
        ToolboxTalkCategory,
        pk=pk
    )

    # FORM SUBMIT
    if request.method == 'POST':

        form = ToolboxTalkCategoryForm(
            request.POST,
            instance=category
        )

        # VALIDATION
        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Category updated successfully.'
            )

            return redirect(
                'toolbox_talk:toolbox_category_list'
            )

    # PAGE LOAD
    else:

        form = ToolboxTalkCategoryForm(
            instance=category
        )

    context = {
        'form': form,
        'category': category
    }

    return render(
        request,
        'toolbox_talk/update_category.html',
        context
    )


def toolbox_category_delete(request, pk):

    """
    Delete Toolbox Talk Category

    Developed by Rajan
    """

    category = get_object_or_404(
        ToolboxTalkCategory,
        pk=pk
    )

    # DELETE CONFIRM
    if request.method == 'POST':

        category.delete()

        messages.success(
            request,
            'Category deleted successfully.'
        )

        return redirect(
            'toolbox_talk:toolbox_category_list'
        )

    context = {
        'category': category
    }

    return render(
        request,
        'toolbox_talk/delete_category.html',
        context
    )