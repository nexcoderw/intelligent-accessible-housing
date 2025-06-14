from users.forms import *
from backend.models import *
from django.db.models import Q, IntegerField
from django.db.models.functions import Cast
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def dashboard(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    user = request.user

    # Application metrics
    total_apps       = RentApplication.objects.filter(user=user).count()
    pending_apps     = RentApplication.objects.filter(user=user, status='Pending').count()
    accepted_apps    = RentApplication.objects.filter(user=user, status='Accepted').count()
    rejected_apps    = RentApplication.objects.filter(user=user, status='Rejected').count()
    moved_out_apps   = RentApplication.objects.filter(user=user, status='Moved Out').count()

    # Contract metrics
    total_contracts  = Contract.objects.filter(tenant=user).count()
    active_contracts = Contract.objects.filter(tenant=user, status='Active').count()
    overdue_contracts= Contract.objects.filter(tenant=user, payment_status='Overdue').count()

    context = {
        'total_apps': total_apps,
        'pending_apps': pending_apps,
        'accepted_apps': accepted_apps,
        'rejected_apps': rejected_apps,
        'moved_out_apps': moved_out_apps,
        'total_contracts': total_contracts,
        'active_contracts': active_contracts,
        'overdue_contracts': overdue_contracts,
        # for Chart.js
        'status_labels': ['Pending','Accepted','Rejected','Moved Out'],
        'status_data': [pending_apps, accepted_apps, rejected_apps, moved_out_apps],
    }
    return render(request, 'backend/pages/users/dashboard.html', context)

@login_required
def search(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    # On initial GET, load choices from the database
    if request.method == 'GET':
        context = {
            'city_choices': Property.CITY_CHOICES,
            'property_types': Property.TYPE_CHOICES,
            'property_categories': Category.objects.all(),
            'amenities_list': Amenity.objects.all(),
        }
        return render(request, 'backend/pages/users/search.html', context)

    # Handle form submission
    if request.method == 'POST':
        filter_params = {
            'city': request.POST.get('city', ''),
            'type': request.POST.get('type', ''),
            'category': request.POST.get('category', ''),  # now an ID
            'capacity': request.POST.get('capacity', ''),
            'bathroom': request.POST.get('bathroom', ''),
            'size': request.POST.get('size', ''),
            'address': request.POST.get('address', ''),
            'price_min': request.POST.get('price_min', ''),
            'price_max': request.POST.get('price_max', ''),
        }
        # collect amenities IDs
        amenities = request.POST.getlist('amenities')
        if amenities:
            filter_params['amenities'] = amenities

        # build querystring
        qs = '&'.join(f"{k}={v}" for k,v in filter_params.items() if v)
        return redirect(f"{reverse('users:properties')}?{qs}")

@login_required
def properties(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    params = request.GET
    qs = Property.objects.all()

    # City
    city = params.get('city')
    if city:
        qs = qs.filter(city__iexact=city)

    # Property Type
    prop_type = params.get('type')
    if prop_type:
        qs = qs.filter(type__iexact=prop_type)

    # Category by ID
    cat = params.get('category')
    if cat:
        try:
            qs = qs.filter(category_id=int(cat))
        except ValueError:
            pass

    # Bedrooms <=
    capacity = params.get('capacity')
    if capacity:
        try:
            qs = qs.filter(capacity__lte=int(capacity))
        except ValueError:
            pass

    # Bathrooms <=
    bathroom = params.get('bathroom')
    if bathroom:
        try:
            qs = qs.filter(bathroom__lte=int(bathroom))
        except ValueError:
            pass

    # Size (assumes `size` stores a plain number as string)
    size_val = params.get('size')
    if size_val:
        try:
            max_size = int(size_val)
            qs = qs.annotate(
                size_int=Cast('size', IntegerField())
            ).filter(size_int__lte=max_size)
        except ValueError:
            pass

    # Address contains
    address = params.get('address')
    if address:
        qs = qs.filter(address__icontains=address)

    # Price range
    price_min = params.get('price_min')
    if price_min:
        try:
            qs = qs.filter(price_usd__gte=int(price_min))
        except ValueError:
            pass

    price_max = params.get('price_max')
    if price_max:
        try:
            qs = qs.filter(price_usd__lte=int(price_max))
        except ValueError:
            pass

    # Amenities ⩽
    amenities = params.getlist('amenities')
    if amenities:
        try:
            amenity_ids = [int(a) for a in amenities]
            qs = qs.filter(amenities__id__in=amenity_ids).distinct()
        except ValueError:
            pass

    # Sorting
    sort = params.get('sort', '').lower()
    if sort == 'oldest':
        qs = qs.order_by('created_at')
    else:
        qs = qs.order_by('-created_at')

    # Pagination
    try:
        limit = int(params.get('limit', 12))
    except ValueError:
        limit = 12

    paginator = Paginator(qs, limit)
    page = params.get('page')
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    context = {
        'properties': page_obj,
        'filter_params': params,
        'properties_count': paginator.count,
        'paginator': paginator,
        'page_obj': page_obj,
    }

    return render(request, 'backend/pages/users/properties/index.html', context)

@login_required
def notifications(request):
    # Only 'User' or superuser can access
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view notifications."))

    context = {}

    if request.user.role == 'User':
        # New properties (last 10)
        new_properties = Property.objects.order_by('-created_at')[:10]

        # User's own rent applications (last 10)
        user_apps = RentApplication.objects.filter(user=request.user).order_by('-created_at')[:10]

        # Contracts received by user (last 10)
        user_contracts = Contract.objects.filter(tenant=request.user).order_by('-created_at')[:10]

        context.update({
            'notif_type': 'user',
            'new_properties': new_properties,
            'user_apps': user_apps,
            'user_contracts': user_contracts,
        })

    else:  # House Provider
        # Contracts on this provider's properties that have been accepted (last 10)
        accepted_contracts = Contract.objects.filter(
            property__created_by=request.user,
            status='Accepted'
        ).order_by('-updated_at')[:10]

        context.update({
            'notif_type': 'provider',
            'accepted_contracts': accepted_contracts,
        })

    return render(request, 'backend/pages/users/notifications.html', context)

@login_required
def getApplications(request):
    applications = RentApplication.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'applications': applications,
    }

    return render(request, 'backend/pages/users/rent-applications/index.html', context)

@login_required
def sendApplication(request, id):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    property_obj = get_object_or_404(Property, id=id)

    # Check if the user has already applied to this property
    existing_application = RentApplication.objects.filter(
        user=request.user,
        property=property_obj
    ).first()

    # If there's an existing application, check the status
    if existing_application:
        if existing_application.status in ['Pending', 'Accepted']:
            messages.warning(request, "You have already applied for this property.")
            return redirect('backend:showProperty', id=id)
        elif existing_application.status in ['Rejected', 'Moved Out']:
            # Allow the user to reapply if the status is Rejected or Moved Out
            pass
        else:
            messages.warning(request, "Invalid application status.")
            return redirect('backend:showProperty', id=id)

    # If the user has not applied yet or has a rejected/moved-out application, allow them to apply
    if request.method == 'POST':
        form = RentApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.property = property_obj
            application.save()

            messages.success(request, "Your rent application has been submitted successfully.")
            return redirect('backend:showProperty', id=id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RentApplicationForm()

    context = {
        'form': form,
        'property': property_obj,
    }

    return render(request, 'backend/pages/users/rent-applications/create.html', context)

@login_required
def getContracts(request):
    """
    Retrieve all contracts for the logged-in user.
    """
    contracts = Contract.objects.filter(tenant=request.user).order_by('-created_at')

    context = {
        'contracts': contracts,
    }

    return render(request, 'backend/pages/users/contracts/index.html', context)

@login_required
def acceptContract(request, contract_id):
    """
    Accept the contract and update its status to 'Active' and payment status to 'Paid'.
    """
    contract = get_object_or_404(Contract, id=contract_id)

    if contract.rent_application.user != request.user:
        messages.error(request, "You don't have permission to sign this contract.")
        return redirect('users:getContracts')

    # Update contract fields
    contract.status = 'Active'
    contract.payment_status = 'Paid'
    contract.signed_date = timezone.now()

    contract.save()

    messages.success(request, "Contract has been signed successfully.")
    return redirect('users:getContracts')