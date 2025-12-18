from django.shortcuts import render
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control




from app.models import *

# Create your views here.
@never_cache
def home(request):
    return render(request, 'home.html')



@never_cache
def about(request):
    return render(request, 'about.html')



@never_cache
def services(request):
    return render(request, 'services.html')


@never_cache
def contact(request):
    return render(request, 'contact.html')




@login_required(login_url='login')
@never_cache
def logout_user(request):
    logout(request)              # Django logout
    request.session.flush()      # Clear session
    messages.success(request, "Logged out successfully.")
    return redirect('login')     # Redirect to login page




@csrf_exempt
@never_cache
def login(request):
    if request.method == "POST":
        uname = request.POST['uname']
        password = request.POST['password']
        a = User.objects.filter(username=uname).first()
        if a:
            if uname==a.username:

                user = authenticate(request, username=uname, password=password)
                print("USER : ", user)

                if user is not None:
                    auth_login(request, user)
                    request.session['user_id'] = user.id  # Auth user ID

                    if user.groups.filter(name='lawyer').exists():
                        return redirect('lawyer_home')
                        
                    elif user.groups.filter(name='testator').exists():

                        testator = Testator.objects.get(USER=user)

                        # ✅ Check approval status
                        if testator.approval_status.lower() == 'approved':
                            request.session['testator'] = testator.id
                            return redirect('testator_home')
                        else:
                            messages.warning(
                                request,
                                f"Your  profile is not approved yet. Current status: {testator.approval_status}."
                            )
                            return redirect('login')
                        
                    elif user.groups.filter(name='beneficiary').exists():

                        will = Will_document.objects.get(USER=user)
                        # beneficiary = Beneficiary.objects.get(WILL_DOCUMENT=will)
                        # request.session['beneficiary'] = beneficiary.id
                        request.session['will'] = will.id
                        return redirect('beneficiary_home')
       
                    else:
                        messages.error(request, 'Invalid user')
                        return redirect('login')
                else:
                    messages.error(request, 'Username or password incorrect')
            else:
                    messages.error(request, 'Invalid username')
                    return redirect('login')
            
        else:
            messages.error(request, 'No such user exist in this platform')
            return redirect('login')
    return render(request, 'login.html')





@never_cache
@csrf_exempt
def testator_register(request):
    if request.method == "POST":
        fullname=request.POST['fullname']
        email=request.POST['email']
        phone=request.POST['phone']
        place=request.POST['place']
        address=request.POST['address']
        idproof=request.FILES['idproof']
        username=request.POST['username']
        password=request.POST['password']
       
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('testator_register')

        # Create user using Django's auth system
        user = User.objects.create_user(username=username, password=password)
        user.save()

        try:
            group = Group.objects.get(name='testator')
        except Group.DosNotExist:
            group = Group.objects.create(name='testator')
        user.groups.add(group)

        # Create care center profile
        Testator.objects.create(
            USER=user,
            full_name=fullname,
            email=email,   
            phone=phone,
            place=place,
            address=address,
            id_proof=idproof,
            death_certificate='pending',
            deceased_date='pending',
            status='active',
            approval_status='pending',

        )

        messages.success(request, 'Registration Completed. Please wait for the approval.')

    return render(request, 'testator_register.html')







#==============================================================  LAWYER  =================================================================



@login_required(login_url='login')
@never_cache
def lawyer_home(request):
    return render(request, 'lawyer_home.html')



@login_required(login_url='login')
@never_cache
def lawyer_verify_testator(request):
    a=Testator.objects.all()
    return render(request, 'lawyer_verify_testator.html', {'a': a})


def lawyer_approve_testator(request,id):
    a=Testator.objects.get(id=id)
    a.approval_status="approved"
    a.save()
    messages.success(request, 'Testator Approved.')
    return redirect('lawyer_verify_testator')


def lawyer_reject_testator(request,id):
    a=Testator.objects.get(id=id)
    a.approval_status="rejected"
    a.save()
    messages.success(request, 'Ship Owner Rejected.')
    return redirect('lawyer_verify_testator')






@login_required(login_url='login')
@never_cache
def lawyer_view_testator(request):
    data = Testator.objects.filter(approval_status='approved')
    return render(request, 'lawyer_view_testator.html', {'a': data})


# # ---------------------------------------------------------
# #  LAWYER — UPDATE STATUS TO DECEASED
# # ---------------------------------------------------------




@login_required(login_url='login')
def update_status(request):
    if request.method == "POST":
        tid = request.POST['tid']
        deceased_date = request.POST['deceased_date']
        file = request.FILES['death_certificate']

        # Fetch testator
        t = Testator.objects.get(id=tid)

        # Update testator status & save file
        t.status = "deceased"
        t.deceased_date = deceased_date
        t.death_certificate = file
        t.save()

        # -----------------------------
        # CREATE NOTIFICATION ENTRY
        # -----------------------------
        try:
            # Get the will of the testator (ONLY ONE WILL PER TESTATOR)
            will = Will_document.objects.get(TESTATOR=t)

            # message_text = (
            #     f"The testator {t.full_name} has been marked deceased on {deceased_date}. "
            #     f"As per the registered will, here is the encryption key: {will.encryption_key}."
            # )

            message_text = (
                f"We regret to inform you that {t.full_name} has passed away on {deceased_date}. "
                f"You have been named as a beneficiary in their last will and testament, which was "
                f"registered on {will.date}. The will document is now available for your access. "
                
            )

            Notification.objects.create(
                WILL_DOCUMENT = will,
                message = message_text,
                date = deceased_date
            )
        
        except Will_document.DoesNotExist:
            # If no will exists, still create a notification
            Notification.objects.create(
                WILL_DOCUMENT=None,
                message=f"The testator {t.full_name} has been marked deceased on {deceased_date}, but no will was found.",
                date=deceased_date
            )

        return redirect('lawyer_view_testator')





# ---------------------------------------------------------
#  BENEFICIARY / LAWYER — DECRYPT WILL
# ---------------------------------------------------------
def decrypt_will(request, tid):

    if request.method != "POST":
        return HttpResponse("Invalid request method", status=405)

    input_key = request.POST['key']

    t = Testator.objects.get(id=tid)

    # Ensure ONLY ONE WILL
    will = Will_document.objects.filter(TESTATOR=t).first()
    if not will:
        return HttpResponse("No will found for this testator")

    if input_key != will.encryption_key:
        return HttpResponse("Invalid key")

    try:
        f = Fernet(input_key.encode())

        with open(will.file.path, "rb") as enc_file:
            encrypted_data = enc_file.read()

        decrypted_data = f.decrypt(encrypted_data)

    except InvalidToken:
        return HttpResponse("Decryption failed — wrong key", status=400)

    # correct file name + mime
    filename = os.path.basename(will.file.name)
    mime, _ = mimetypes.guess_type(filename)
    if not mime:
        mime = "application/octet-stream"

    file_obj = io.BytesIO(decrypted_data)
    file_obj.seek(0)

    return FileResponse(file_obj, filename=filename, content_type=mime)




from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from django.utils import timezone
from .models import Upload, Will_document
import hashlib

def get_file_hash2(uploaded_file):
    hash_sha = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        hash_sha.update(chunk)
    return hash_sha.hexdigest()


@csrf_exempt
@never_cache
def uplaod_file(request):
    result = None
    uploaded_hash = None
    original_hash = None
    matched_user = None

    if request.method == "POST":
        uploaded_file = request.FILES['file']

        # 1) Hash of uploaded file
        uploaded_hash = get_file_hash2(uploaded_file)

        # 2) Check if this hash exists in any Will_document
        matching_will = Will_document.objects.filter(file_hash=uploaded_hash).first()

        if matching_will:
            original_hash = matching_will.file_hash
            matched_user = matching_will.USER.username  # or name field
            result = f"✔ Authentic – Matches the original document of user: {matched_user}"
        else:
            result = "❌ Not Authentic – No matching original document found."

        # Save upload for record
        Upload.objects.create(
            USER=request.user if request.user.is_authenticated else None,
            uploaded_file=uploaded_file,
            result=result,
            date=str(timezone.now())
        )

        return render(request, "uplaod_file.html", {
            "result": result,
            "uploaded_hash": uploaded_hash,
            "original_hash": original_hash,
            "matched_user": matched_user,
        })

    return render(request, "uplaod_file.html")






#==============================================================  TESTATOR  =================================================================



@login_required(login_url='login')
@never_cache
def testator_home(request):
    return render(request, 'testator_home.html')



import os
import io
import mimetypes
import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime

from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User, Group
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from .models import Will_document, Beneficiary, Testator


# ---------------------------------------------------------
#  HASH FUNCTION
# ---------------------------------------------------------
def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------
#  CUSTOM EMAIL SENDER (SMTP)
# ---------------------------------------------------------
def send_custom_email(to_email, subject, body):
    sender = "safedore3@gmail.com"
    password = "yqqlwlyqbfjtewam"   # Gmail App Password

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
        print("Email sent →", to_email)
        return True
    except Exception as e:
        print("Email failed:", e)
        return False


# ---------------------------------------------------------
#  TESTATOR — UPLOAD WILL  +  ADD BENEFICIARIES
# ---------------------------------------------------------
@login_required(login_url='login')
def testator_add_will(request):

    try:
        testator = Testator.objects.get(USER=request.user)
        
        # Check if testator status is active
        if testator.status != 'active':
            messages.error(request, "You cannot upload a will. Your status is marked as deceased.")
            return redirect("testator_home")  # or wherever you want to redirect
            
    except Testator.DoesNotExist:
        messages.error(request, "Testator profile not found.")
        return redirect("testator_home")

    if request.method == "POST":

        testator = Testator.objects.get(USER=request.user)

        # 🍀 Ensure ONE WILL PER TESTATOR
        existing = Will_document.objects.filter(TESTATOR=testator).first()
        if existing:
            messages.error(request, "You already uploaded a will. Only one will is allowed.")
            return redirect("testator_add_will")

        uploaded_file = request.FILES['file']
        desc = request.POST['desc']
        username = request.POST['username']
        password = request.POST['password']

        # 1️⃣ Create login user for this will
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("testator_add_will")

        user = User.objects.create_user(username=username, password=password)

        # Add user to beneficiary group
        group, created = Group.objects.get_or_create(name='beneficiary')
        user.groups.add(group)
        user.save()

        # 2️⃣ Save will record
        will = Will_document.objects.create(
            USER=user,
            TESTATOR=testator,
            file=uploaded_file,
            description=desc,
            date=str(datetime.now())
        )

        # 3️⃣ Hashing
        file_path = will.file.path
        will.file_hash = get_file_hash(file_path)

        # 4️⃣ Encrypt file
        key = Fernet.generate_key()
        fernet = Fernet(key)

        with open(file_path, "rb") as f:
            original_bin = f.read()

        encrypted_bin = fernet.encrypt(original_bin)

        with open(file_path, "wb") as f:
            f.write(encrypted_bin)

        will.encryption_key = key.decode()
        will.save()

        # 5️⃣ Save Beneficiaries + Email credentials
        names = request.POST.getlist("b_name[]")
        emails = request.POST.getlist("b_email[]")
        places = request.POST.getlist("b_place[]")

        for n, e, p in zip(names, emails, places):

            Beneficiary.objects.create(
                WILL_DOCUMENT=will,
                name=n,
                email=e,
                place=p
            )

#             email_body = f"""
# Hello {n},

# You have been added as a beneficiary in the Digital Will system.

# Login Credentials:
# --------------------------
# Username: {username}
# Password: {password}
# --------------------------

# You will be able to access the will after the testator is marked as deceased.

# Regards,
# Digital Will System
# """
            email_body = f"""
            Dear {n},

            We are writing to inform you that you have been designated as a beneficiary in our Digital Will Management System.

            BENEFICIARY DETAILS
            ━━━━━━━━━━━━━━━━━━━
            Name: {n}
            Email: {e}
            Place: {p}

            SECURE ACCESS CREDENTIALS
            ━━━━━━━━━━━━━━━━━━━
            Username: {username}
            Password: {password}

            IMPORTANT INFORMATION
            ━━━━━━━━━━━━━━━━━━━
            - Please keep these credentials secure and confidential
            - Access to the will document will be granted upon verification of the testator's deceased status
            - You will receive a notification when the document becomes available for viewing

            NEXT STEPS
            ━━━━━━━━━━━━━━━━━━━
            1. Store these credentials in a secure location
            2. Do not share your login information with anyone
            3. Contact our support team if you have any questions or concerns


            Warm regards,

            Digital Will Management System
            Security & Compliance Team

            ━━━━━━━━━━━━━━━━━━━
            This is an automated message. Please do not reply to this email.
            For support, contact: [support@dwats.com]
            © {datetime.now().year} Digital Will Management System. All rights reserved.
            """

            send_custom_email(
                to_email=e,
                subject="Digital Will – Beneficiary Access",
                body=email_body
            )

        messages.success(request, "Will uploaded, encrypted, and beneficiary emails sent!")
        return redirect("testator_add_will")

    return render(request, "testator_add_will.html")



#==============================================================  TESTATOR  =================================================================


@login_required(login_url='login')
@never_cache
def beneficiary_home(request):
    # Get will_id from session
    will_id = request.session.get('will')
    
    # Get notifications for this will
    a = Notification.objects.filter(WILL_DOCUMENT_id=will_id)
    
    # Get the will document (only if notifications exist)
    b = None
    c = None
    
    if will_id:
        try:
            b = Will_document.objects.get(id=will_id)
            c = Testator.objects.get(id=b.TESTATOR_id)
        except (Will_document.DoesNotExist, Testator.DoesNotExist):
            pass
    
    return render(request, 'beneficiary_home.html', {'a': a, 'b': b, 'c': c})
