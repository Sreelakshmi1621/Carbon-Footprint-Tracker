from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import Asset, Usage,Factory ,FactoryProfile
from django.utils import timezone
from django.http import JsonResponse      # <-- add this import at the top of views.py
from django.db.models import Sum
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from .forms import FactoryProfileForm
from django.contrib.auth import update_session_auth_hash
from django.db.models.functions import TruncMonth
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from .models import Factory, Asset, Usage, Notification
from django.utils.dateparse import parse_date
import csv
from django.http import HttpResponse
from .models import AdminProfile
from django.db.models import Sum
from .models import Factory, Notification, Report, Usage
#from factoryapp.models import Factory, Notification
from django.utils.timezone import now
from django.core.mail import send_mail



# Emission factors constant dictionary
FUEL_FACTORS = {
    "electricity": 0.85,
    "diesel": 2.68,
    "petrol": 2.31,
    "lpg": 1.51,
    "natural-gas": 2.04,
    "other": 1.0
}

def homepage(request):
    # This view renders your homepage
    return render(request, 'factory/home.html')


def register(request):
    return render(request, 'factory/register.html')


def login_view(request):
    return render(request, 'factory/login.html')

def forgot_password(request):
    return render(request, 'factory/forgot-password.html')

def add_factoryprofile(request):
    return render(request, "factory/add_factoryprofile.html")

# views.py
from django.shortcuts import render

def add_factoryprofile(request):
    return render(request, 'add_factoryprofile/index.html')



def add_asset(request):
    return render(request, "factory/add-asset.html")


def add_usage(request):
    # For now, just render the HTML page
    return render(request, "factory/add_usage.html")

def reports_page(request):
    """
    This view simply renders the Reports HTML page with filters and table.
    """
    return render(request, "factory/reports.html")






def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password1 = request.POST.get("password")
        password2 = request.POST.get("confirm_password")

        # Prepare context to preserve input values
        context = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }

        # Password match check
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "factory/register.html", context)

        # Password validations
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "factory/register.html", context)

        if not any(char.isdigit() for char in password1):
            messages.error(request, "Password must contain at least one number.")
            return render(request, "factory/register.html", context)

        if not any(char.isupper() for char in password1):
            messages.error(request, "Password must contain at least one uppercase letter.")
            return render(request, "factory/register.html", context)

        if not any(char in "!@#$%^&*" for char in password1):
            messages.error(request, "Password must contain at least one special character (!@#$%^&*).")
            return render(request, "factory/register.html", context)

        # Email duplication check
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "factory/register.html", context)

        # Create new user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        # ✅ Send registration success email
        send_mail(
           subject='Welcome to Carbon Footprint Tracker!',
           message='Hello! Your registration was successful!...You can now log in and start tracking your factory emissions easily.',
           from_email='trackercarbonfootprint@gmail.com',
           recipient_list=[email],
           fail_silently=False,
        )


        # Success message
       # After user.save()
        messages.success(request, "Registration successful! You can now login.")
        return redirect('register')  # redirect to the same page or to login
        # Clear input fields after successful registration
        context = {}
        return render(request, "factory/register.html", context)

    # GET request
    return render(request, "factory/register.html")





def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)  # log the user in

                    # ✅ Step 1: Check if the user is admin
            if user.is_superuser:
                return redirect('admin_dashboard')  # redirects to admin dashboard    

            # Check if the user has any factories
            factories = Factory.objects.filter(owner=user)
            
            if not factories.exists():
                # No factories yet → redirect to Add Factory Profile
                return redirect('add_factoryprofile')
            elif factories.count() == 1:
                request.session['active_factory_id'] = factories.first().id
                return redirect('factory_dashboard')
            else:
                # 2+ factories → show selection page
                return redirect('select_factory')


        else:
            messages.error(request, "Invalid email or password.")
            return render(request, "factory/login.html")

    return render(request, "factory/login.html")




def add_factoryprofile(request):
    if request.method == "POST":
        factory_name = request.POST.get("factoryName")
        factory_type = request.POST.get("factoryType")
        reg_number = request.POST.get("regNumber")
        est_year = int(request.POST.get("estYear"))  # convert to int
        address = request.POST.get("address")
        city = request.POST.get("city")
        country = request.POST.get("country")
        phone = request.POST.get("phone")  # convert if IntegerField: int(phone)
        email = request.user.email  

        Factory.objects.create(
            owner=request.user,   # ✅ correct field
            name=factory_name,    # ✅ correct field
            factory_type=factory_type,
            registration_number=reg_number,
            established_year=est_year,
            address=address,
            city=city,
            country=country,
            phone_number=phone,   # ✅ correct field
            email=email
        
        )

        request.session['added_from_dashboard'] = True
        return redirect("factory_dashboard")


    return render(request, "factory/add_factoryprofile.html")




@login_required
def factory_dashboard(request):
    factories = Factory.objects.filter(owner=request.user)
    
    total_factories = factories.count()

    if not factories.exists():
        return redirect("add_factoryprofile")

    # Determine which factory to display
    active_factory_id = request.session.get('active_factory_id')
    if active_factory_id:
        factory = get_object_or_404(Factory, id=active_factory_id, owner=request.user)
    elif factories.count() == 1:
        factory = factories.first()
        request.session['active_factory_id'] = factory.id

    else:
        # Multiple factories, no active selection → go to selection page
        return redirect("select_factory")

    # ------------------------
    # Dashboard calculations
    # ------------------------
    total_assets = Asset.objects.filter(factory=factory).count()
    total_emissions = Usage.objects.filter(asset__factory=factory).aggregate(total=Sum('emission'))['total'] or 0

    current_year = date.today().year
    monthly_data = Usage.objects.filter(asset__factory=factory, date__year=current_year)\
        .annotate(month=TruncMonth('date'))\
        .values('month')\
        .annotate(monthly_total=Sum('emission'))\
        .order_by('month')

    if monthly_data:
        monthly_average = round(sum(item['monthly_total'] for item in monthly_data) / len(monthly_data), 2)
    else:
        monthly_average = 0   

    chart_labels = [item['month'].strftime("%b") for item in monthly_data]
    chart_data = [round(item['monthly_total'], 2) for item in monthly_data]

    compliance_status = "Good"
    unread_notifications = Notification.objects.filter(factory_owner=request.user, is_read=False).count()

    recent_assets = Asset.objects.filter(factory=factory).order_by('-created_at')[:5]
    recent_usages = Usage.objects.filter(asset__factory=factory).order_by('-created_at')[:5]
    recent_notifications = Notification.objects.filter(factory_owner=request.user).order_by('-created_at')[:5]

    recent_activity = []

    for asset in recent_assets:
        recent_activity.append({
            'type': 'asset', 
            'name': asset.name,
            'timestamp': asset.created_at,
        })
    for usage in recent_usages:
        recent_activity.append({
            'type': 'usage',
            'name': usage.asset.name, 
            'timestamp': usage.created_at,
        })
    for notif in recent_notifications:
        recent_activity.append({
            'type': 'notification',
            'name': notif.title,
            'timestamp': notif.created_at,})

    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activity = recent_activity[:5]

    context = {
        "factory": factory,
        "total_assets": total_assets,
        "total_emissions": total_emissions,
        "monthly_average": monthly_average,
        "compliance_status": compliance_status,
        "unread_notifications": unread_notifications,
        "recent_activity": recent_activity,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "total_factories": total_factories,  # ✅ add here for template

    }

    return render(request, "factory/factory_dashboard.html", context)


@login_required
def add_asset(request):
    active_factory_id = request.session.get('active_factory_id')
    if not active_factory_id:
        # If no factory selected, redirect to factory selection
        return redirect('select_factory')

    factory = get_object_or_404(Factory, id=active_factory_id, owner=request.user)

    if request.method == "POST":
        name = request.POST.get('assetName')
        asset_type = request.POST.get('assetType')
        fuel_type = request.POST.get('fuelType')
        unit = request.POST.get('unit')

        # ✅ Always get emission factor correctly
        emission_factor = FUEL_FACTORS.get(fuel_type.lower().strip(), 1.0)

        # Save asset
        Asset.objects.create(
            factory=factory,
            name=name,
            asset_type=asset_type,
            fuel_type=fuel_type,
            unit=unit,
            emission_factor=emission_factor
        )

        messages.success(
            request,
            f"✅ Asset '{name}' added successfully with emission factor {emission_factor} kg CO₂/unit!"
        )
        return redirect('add_asset')

    return render(request, "factory/add_asset.html")



def add_usage(request):
    # Get all assets for this user’s factories
    user_factories = Factory.objects.filter(owner=request.user)
    assets = Asset.objects.filter(factory__in=user_factories)

    if request.method == "POST":
        asset_id = request.POST.get('asset_id')
        consumption = request.POST.get('usage_amount')
        usage_date = request.POST.get('date')

        # Validation
        if not asset_id or not consumption or not usage_date:
            messages.error(request, "⚠️ Please fill all required fields.")
            return redirect('add_usage')

        try:
            asset = Asset.objects.get(id=asset_id)
            consumption = float(consumption)
        except Exception as e:
            print("Error:", e)
            messages.error(request, "Invalid asset or consumption value.")
            return redirect('add_usage')

        # ✅ Emission calculation (correct)
        emission = round(consumption * asset.emission_factor, 2)

        # Debug print (for VS Code console check)
        print(f"[DEBUG] {asset.name}: Consumption={consumption}, Factor={asset.emission_factor}, Emission={emission}")

        # Save usage record
        Usage.objects.create(
            asset=asset,
            date=usage_date,
            usage_amount=consumption,
            emission=emission,
        )

        messages.success(
            request,
            f"✅ Usage for '{asset.name}' added successfully! Emission: {emission} kg CO₂"
        )
        return redirect('add_usage')

    return render(request, 'factory/add_usage.html', {'assets': assets})



# ==============================
# STEP 1: Reports Backend View
# ==============================

def generate_report(request):
    """
    This view returns emission report data (in JSON) 
    for the logged-in user's factories, filtered by date range.
    """

    active_factory_id = request.session.get('active_factory_id')
    if not active_factory_id:
        return JsonResponse({"status": "error", "message": "No factory selected."})

    factory = get_object_or_404(Factory, id=active_factory_id, owner=request.user)

    # Filter usage only for this factory
    usages = Usage.objects.filter(asset__factory=factory)


    # ✅ Step 3: Apply date filter if provided
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date and end_date:
        # convert to date objects for filtering
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        usages = usages.filter(date__range=[start, end])

    # ✅ Step 4: Prepare data for JSON response
    data = []
    for usage in usages:
        data.append({
            "asset": usage.asset.name,
            "asset_type": usage.asset.asset_type,
            "fuel_type": usage.asset.fuel_type,
            "date": usage.date.strftime("%Y-%m-%d"),
            "usage_amount": usage.usage_amount,
            "emission": usage.emission,
        })

    # ✅ Step 5: Calculate totals
    total_emission = usages.aggregate(total=Sum("emission"))["total"] or 0

    # ✅ Step 6: Return everything as JSON
    return JsonResponse({
        "data": data,
        "total_emission": total_emission,
        "count": usages.count(),
    })



@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(factory_owner=request.user).order_by('-created_at')
    return render(request, 'factory/notifications.html', {'notifications': notifications})



@login_required
@require_POST
def mark_notification_read(request):
    notif_id = request.POST.get("notif_id")

    if not notif_id:
        return JsonResponse({"status": "error", "message": "No notification ID provided."})

    try:
        notif = Notification.objects.get(id=notif_id, factory_owner=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({"status": "success"})
    except Notification.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Notification not found."})

    

@login_required
@require_POST
def delete_notification(request):
    notif_id = request.POST.get("notif_id")

    if not notif_id:
        return JsonResponse({"status": "error", "message": "No notification ID provided."})

    try:
        notif = Notification.objects.get(id=notif_id, factory_owner=request.user)
        notif.delete()
        return JsonResponse({"status": "success"})
    except Notification.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Notification not found."})




# ✅ View to display and update Factory Profile

@login_required
def factory_profile_view(request, factory_id):
    factory = get_object_or_404(Factory, id=factory_id, owner=request.user)

    # Define the list of factory types
    factory_types = [
        "Textile / Garment",
        "Cement / Concrete",
        "Steel / Metal Processing",
        "Chemical / Pharmaceutical",
        "Plastic / Polymer",
        "Electronics / Electrical",
        "Food Processing",
        "Beverage / Brewery",
        "Power Plant",
        "Oil & Gas Refinery",
        "Paper & Pulp",
        "Automobile / Vehicle Assembly",
        "Furniture / Wood Products",
        "Other",
    ]

    if request.method == "POST":
        form = FactoryProfileForm(request.POST,request.FILES, instance=factory)
        if form.is_valid():
            form.save()
            messages.success(request, "Factory profile updated successfully!")  # ✅ add this

    else:
        form = FactoryProfileForm(instance=factory)

    # Pass the list to the template
    context = {
        'form': form,
        'factory': factory,
        'factory_types': factory_types,  # ✅ here
    }

    return render(request, 'factory/factory_profile.html', context)


@login_required
def change_password(request):
    """
    Allows the logged-in user to change their password.
    - Verifies current password
    - Validates new password and confirmation
    - Updates password securely
    """
    if request.method == "POST":
        current_password = request.POST.get("currentPassword")
        new_password = request.POST.get("newPassword")
        confirm_password = request.POST.get("confirmPassword")
        user = request.user

        # 1️⃣ Check current password
        if not user.check_password(current_password):
            messages.error(request, "⚠️ Current password is incorrect!")
            return redirect("change_password")

        # 2️⃣ Check new password matches confirmation
        if new_password != confirm_password:
            messages.error(request, "❌ New password and confirm password do not match!")
            return redirect("change_password")

        # 3️⃣ Optional: check password strength
        import re
        password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(password_regex, new_password):
            messages.error(request, "❌ Password must be at least 8 characters and include uppercase, lowercase, number, and special character.")
            return redirect("change_password")

        # 4️⃣ Update password securely
        user.set_password(new_password)
        user.save()

        # 5️⃣ Keep user logged in after password change
        update_session_auth_hash(request, user)

        # 6️⃣ Success message
        messages.success(request, "✅ Password updated successfully!")

        return redirect("change_password")

    return render(request, "factory/change_password.html")



@login_required
@require_POST
def request_account_closure(request):
    """
    Handles user request for account/factory closure.
    Sends a notification to the admin.
    """
    user = request.user

    # Create a notification for admin
    Notification.objects.create(
        factory_owner=user,  # user who made the request
        title="Account Closure Request",
        message=f"{user.first_name} {user.last_name} ({user.email}) has requested account closure.",
        priority="high"
    )

    return JsonResponse({"status": "success", "message": "Closure request sent to admin."})



from django.contrib.auth import logout

@login_required
@require_POST
def deactivate_account(request):
    """
    Deactivates the user's account and sends a notification to the admin.
    """
    user = request.user

    # Deactivate the user
    user.is_active = False
    user.save()

    # Create a notification for admin
    Notification.objects.create(
        factory_owner=user,
        title="Account Deactivated",
        message=f"{user.first_name} {user.last_name} ({user.email}) has deactivated their account.",
        priority="high"
    )

    # Log out the user immediately
    logout(request)

    return JsonResponse({"status": "success", "message": "Your account has been deactivated and you are logged out."})



@login_required
def account_management_view(request):
    # Get all factories linked to this user
    factories = Factory.objects.filter(owner=request.user)
    return render(request, 'factory/account_management.html', {'factories': factories})


@login_required
def select_factory_view(request):
    # Get all factories for the logged-in user
    factories = Factory.objects.filter(owner=request.user)
    
    return render(request, "factory/factory_selection.html", {"factories": factories})


@login_required
@require_POST
def set_active_factory(request):
    """
    Sets the selected factory in the session and redirects to dashboard.
    """
    factory_id = request.POST.get("factory_id")
    if factory_id:
        factory = get_object_or_404(Factory, id=factory_id, owner=request.user)
        # Store selected factory ID in session
        request.session['active_factory_id'] = factory.id
        return redirect("factory_dashboard")
    
    # If factory_id missing, redirect back with a warning
    messages.warning(request, "No factory selected. Please try again.")
    return redirect("select_factory")

@login_required
def admin_dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('factory_dashboard')  # safety check

    return render(request, 'factory/admin_dashboard.html')

###--------------------------------------------------------------------------------

# ✅ STEP 1: Admin Dashboard View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('factory_dashboard')

    profile, created = AdminProfile.objects.get_or_create(user=request.user)

    total_factories = Factory.objects.count()
# Only messages sent *to admin* and not read yet
# Count only messages coming from factory owners (user → admin)
    active_notifications = Notification.objects.filter(factory_owner__isnull=False, is_read=False).count()
    recent_reports = Report.objects.count()
    emissions_summary = Usage.objects.aggregate(total_emission=Sum('emission'))['total_emission'] or 0
    emissions_summary = round(emissions_summary, 2)
    compliance_status = "Good" if emissions_summary < 10000 else "Needs Attention"

    # === ✅ Monthly Emission Data for Chart ===
    current_year = now().year
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_emissions = []

    for month in range(1, 13):
        total = Usage.objects.filter(date__year=current_year, date__month=month).aggregate(total_emission=Sum('emission'))['total_emission']
        monthly_emissions.append(round(total or 0, 2))
    print("Monthly emissions:", monthly_emissions)


    profile = AdminProfile.objects.get(user=request.user)
    profile_picture_url = profile.profile_picture.url if profile.profile_picture else '/static/factory/images/default_profile.png'

    context = {
        'profile': profile,
        'profile_picture_url': profile_picture_url,
        'user_obj': request.user,
        'total_factories': total_factories,
        'active_notifications': active_notifications,
        'recent_reports': recent_reports,
        'emissions_summary': emissions_summary,
        'compliance_status': compliance_status,
        'months': months,
        'monthly_emissions': monthly_emissions,  # ✅ send to template
    
    }

    return render(request, 'factory/admin_dashboard.html', context)



# ✅ Manage Factories view for admin
# factory/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Factory
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# ✅ Manage Factories view for admin
from django.shortcuts import render, get_object_or_404, redirect
from .models import Factory
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Factory
from django.urls import reverse

@login_required
def manage_factories(request):
    # Only admin users should access
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('login')  # or homepage

    # Fetch all factories from database
    factories = Factory.objects.all()

    # Get unique factory types for dropdown filter
    factory_types = Factory.objects.values_list('factory_type', flat=True).distinct()

    # Pass factories and types to template
    context = {
        'factories': factories,
        'factory_types': factory_types,
    }
    return render(request, 'factory/manage_factories.html', context)


@login_required
def delete_factory(request, factory_id):
    if not request.user.is_superuser:
        return redirect('login')

    factory = get_object_or_404(Factory, id=factory_id)
    factory.delete()
    return redirect('manage_factories')  # No need for reverse if using redirect()





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Factory, Asset, Usage
from django.db.models import Sum
from django.utils.dateparse import parse_date

@login_required
def admin_reports(request):
    if not request.user.is_staff:
        return redirect('login')  # Only admin can access

    factories = Factory.objects.all()
    
    # Only populate data if Generate button clicked (i.e., some filter is applied)
    report_data = None
    top_emitters = None
    selected_factory = ''
    start_date = ''
    end_date = ''

    if 'factory' in request.GET or 'start_date' in request.GET or 'end_date' in request.GET:
        factory_id = request.GET.get('factory')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        selected_factory = factory_id or ''

        usage_qs = Usage.objects.select_related('asset', 'asset__factory')

        if factory_id and factory_id != 'all':
            usage_qs = usage_qs.filter(asset__factory_id=factory_id)
        if start_date:
            usage_qs = usage_qs.filter(date__gte=start_date)
        if end_date:
            usage_qs = usage_qs.filter(date__lte=end_date)

        report_data = usage_qs.values(
            'asset__factory__id',
            'asset__factory__name',
            'date'
        ).annotate(total_emission=Sum('emission')).order_by('date')

        top_emitters = usage_qs.values('asset__factory__name').annotate(
            total_emission=Sum('emission')
        ).order_by('-total_emission')[:3]

    context = {
        'factories': factories,
        'report_data': report_data,
        'top_emitters': top_emitters,
        'selected_factory': selected_factory,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'factory/admin_reports.html', context)



from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.db.models import Sum
from datetime import datetime

@login_required
def admin_reports_pdf(request):
    if not request.user.is_staff:
        return redirect('login')

    # ✅ Get filters
    factory_id = request.GET.get('factory')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    usage_qs = Usage.objects.select_related('asset', 'asset__factory')

    if factory_id and factory_id != 'all':
        usage_qs = usage_qs.filter(asset__factory_id=factory_id)
    if start_date:
        usage_qs = usage_qs.filter(date__gte=start_date)
    if end_date:
        usage_qs = usage_qs.filter(date__lte=end_date)

    # ✅ Prepare PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="emission_report.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # ✅ Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, height - 1 * inch, "Carbon Footprint Tracker - Emission Report")

    # ✅ Subtitle / filter info
    p.setFont("Helvetica", 11)
    y = height - 1.4 * inch
    p.drawString(1 * inch, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 0.3 * inch
    if start_date or end_date:
        p.drawString(1 * inch, y, f"Date range: {start_date or '---'} to {end_date or '---'}")
        y -= 0.3 * inch
    if factory_id and factory_id != 'all':
        factory_name = Factory.objects.get(id=factory_id).name
        p.drawString(1 * inch, y, f"Factory: {factory_name}")
        y -= 0.3 * inch

    # ✅ Table header
    y -= 0.2 * inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, y, "Factory")
    p.drawString(3.5 * inch, y, "Date")
    p.drawString(5.2 * inch, y, "Total Emission (kg CO₂)")
    y -= 0.2 * inch
    p.line(1 * inch, y, 7.5 * inch, y)
    y -= 0.2 * inch

    # ✅ Table rows
    p.setFont("Helvetica", 11)
    for row in usage_qs.values('asset__factory__name', 'date').annotate(total_emission=Sum('emission')).order_by('date'):
        if y < 1 * inch:  # new page if content goes too low
            p.showPage()
            y = height - 1 * inch
            p.setFont("Helvetica", 11)
        p.drawString(1 * inch, y, row['asset__factory__name'])
        p.drawString(3.5 * inch, y, row['date'].strftime('%Y-%m-%d'))
        p.drawRightString(7.2 * inch, y, str(round(row['total_emission'], 2)))
        y -= 0.25 * inch

    p.showPage()
    p.save()

    return response


from django.shortcuts import render, redirect
from .models import Notification, User
from django.contrib.auth.decorators import login_required

@login_required
def admin_announcements(request):
    notifications = Notification.objects.all().order_by('-created_at')  # latest first
    context = {
        'notifications': notifications
    }
    return render(request, 'admin_announcements.html', context)


@login_required
def create_announcement(request):
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        priority = request.POST.get("priority")
        target = request.POST.get("target")  # "all" or user_id

        if target == "all":
            users = User.objects.all()
            for user in users:
                Notification.objects.create(factory_owner=user, title=title, message=message, priority=priority)
        else:
            user = User.objects.get(id=int(target))
            Notification.objects.create(factory_owner=user, title=title, message=message, priority=priority)

        return redirect('admin_announcements')

    users = User.objects.all()
    return render(request, 'create_announcement.html', {'users': users})



# Only admin should access this page
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification, Factory
from django.contrib.auth.models import User
from django.utils import timezone

# Only admin should access this page
@login_required
def admin_notifications_view(request):
    user = request.user

    # Optional: check if user is admin
    if not user.is_staff:
        return redirect('homepage')  # redirect non-admins

    if request.method == "POST":
        # --- 1. Get form data from POST ---
        send_to = request.POST.get("send_to")  # factory id or 'all'
        priority = request.POST.get("priority")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # --- 2. Validate input ---
        if not subject or not message:
            # Here you can send an error message to template instead of just skipping
            return render(request, "admin_notifications.html", {
                "error": "Subject and message cannot be empty.",
                "notifications": Notification.objects.all().order_by('-created_at'),
                "factories": Factory.objects.all()
            })

        # --- 3. Create notifications ---
        if send_to == "all":
            # Send to all factories
            all_factories = Factory.objects.all()
            for factory in all_factories:
                Notification.objects.create(
                    factory_owner=factory.owner,
                    title=subject,
                    message=message,
                    priority=priority,
                    created_at=timezone.now()
                )
        else:
            # Send to selected factory
            try:
                factory = Factory.objects.get(id=int(send_to))
                Notification.objects.create(
                    factory_owner=factory.owner,
                    title=subject,
                    message=message,
                    priority=priority,
                    created_at=timezone.now()
                )
            except Factory.DoesNotExist:
                # Optional: handle invalid factory id
                return render(request, "admin_notifications.html", {
                    "error": "Selected factory does not exist.",
                    "notifications": Notification.objects.all().order_by('-created_at'),
                    "factories": Factory.objects.all()
                })

        # After sending, redirect to the same page to show updated notifications
        messages.success(request, "Notification sent successfully!")

        return redirect("admin_notifications")

    # --- GET request: display notifications page ---
    notifications = Notification.objects.all().order_by('-created_at')  # latest first
    factories = Factory.objects.all()  # for dropdown list

    context = {
        "notifications": notifications,
        "factories": factories
    }

    return render(request, "factory/admin_notifications.html", context)

# factory/views.py


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

# factory/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AdminProfile

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

@login_required
def admin_profile_view(request):
    # Get or create AdminProfile for logged-in user
    profile, created = AdminProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # --- Update Name ---
        name = request.POST.get('name')
        if name:
            profile.name = name
            request.user.first_name = name  # for header/email display
            request.user.save()
        
        # --- Update Profile Picture ---
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()

        # --- Update Password ---
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if old_password or new_password or confirm_password:
            # Only proceed if at least one password field is filled
            if not request.user.check_password(old_password):
                messages.error(request, "Old password is incorrect!")
            elif new_password != confirm_password:
                messages.error(request, "New password and confirm password do not match!")
            else:
                request.user.set_password(new_password)
                request.user.save()
                # Keep user logged in after password change
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password updated successfully!")

        else:
            messages.success(request, "Profile updated successfully!")

        return redirect('admin_profile')

    context = {
        'profile': profile,       # AdminProfile object
        'user_obj': request.user  # User object for email
    }
    return render(request, 'factory/admin_profile.html', context)





from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        AdminProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_admin_profile(sender, instance, **kwargs):
    if instance.is_staff:
        instance.adminprofile.save()
     


def admin_delete_notification(request, notif_id):
    if not request.user.is_superuser:
        return redirect('factory_dashboard')  # only admin can access

    try:
        notif = Notification.objects.get(id=notif_id)
        notif.delete()
        #messages.success(request, "Notification deleted successfully.")
    except Notification.DoesNotExist:
        messages.error(request, "Notification not found.")
    
    return redirect('admin_notifications')
    

#new
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)  # This clears the session
    return redirect('login')  # Redirects to login page


# views.py
# factory/views.py
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User

from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

def forgot_password(request):
    message = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            # Generate token
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)

            # Encode user ID
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            # Build password reset URL
            current_site = get_current_site(request)
            reset_url = f"http://{current_site.domain}{reverse('reset_password_confirm', kwargs={'uidb64': uidb64, 'token': token})}"

            # Send email
            subject = "Reset Your Password - Carbon Footprint Tracker"
            message_body = f"Hello {user.username},\n\nClick the link below to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore this email."
            send_mail(subject, message_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)

            message = 'Reset link sent! Check your email.'
        except User.DoesNotExist:
            message = 'No user found with this email.'

    return render(request, 'factory/forgot-password.html', {'message': message})


from django.shortcuts import render
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User


def reset_password_confirm(request, uidb64, token):
    """
    Placeholder view for token-based password reset.
    We'll later validate the token and allow the user to reset their password.
    """
    return render(request, 'factory/reset_password.html')






from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def reset_password(request, email):
    message = ''
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        message = 'Invalid reset link.'
        return render(request, 'factory/reset-password.html', {'message': message})

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully! You can now login.')
            return redirect('login')
        else:
            message = 'Passwords do not match.'

    return render(request, 'factory/reset-password.html', {'message': message})


from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
def reset_password_confirm(request, uidb64, token):
    message = ''
    token_generator = PasswordResetTokenGenerator()

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is not None and token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if not new_password or not confirm_password:
                message = 'Both fields are required.'
            elif new_password != confirm_password:
                message = 'Passwords do not match.'
            elif len(new_password) < 6:
                message = 'Password must be at least 6 characters long.'
            else:
                user.set_password(new_password)
                user.save()
                message = 'Password reset successful!'
                return redirect('login')
        return render(request, 'factory/reset-password.html', {'message': message})
    else:
        message = 'Invalid or expired link.'
        return render(request, 'factory/reset-password.html', {'message': message})
