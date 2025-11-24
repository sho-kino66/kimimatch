from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings

from .models import Announcement
from .forms import SchoolApplicationForm, CompanyApplicationForm

# お知らせ詳細
@login_required
def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    return render(request, 'core/announcement_detail.html', {'announcement': announcement})

# トップページ
def top_page(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'core/top_page.html')

# 機能紹介ページ
def student_service(request):
    return render(request, 'core/student_service.html')
def company_service(request):
    return render(request, 'core/company_service.html')
def school_service(request):
    return render(request, 'core/school_service.html')

# 申し込み完了画面
def application_success(request):
    return render(request, 'core/application_success.html')

# 学校申し込みフォーム
class SchoolApplicationView(FormView):
    template_name = 'core/school_application_form.html'
    form_class = SchoolApplicationForm
    success_url = reverse_lazy('core:application_success') 

    def form_valid(self, form):
        data = form.cleaned_data
        subject = f"【KimiMatch】学校利用の申し込み: {data['school_name']}"
        message = f"学校名: {data['school_name']}\n担当者: {data['contact_name']}\nEmail: {data['email']}\nTel: {data['phone']}\n住所: {data['address']}"
        
        superuser_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
        if superuser_emails:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, superuser_emails, fail_silently=False)
            
        return super().form_valid(form)

# 企業申し込みフォーム
class CompanyApplicationView(FormView):
    template_name = 'core/company_application_form.html'
    form_class = CompanyApplicationForm
    success_url = reverse_lazy('core:application_success') 

    def form_valid(self, form):
        data = form.cleaned_data
        subject = f"【KimiMatch】企業利用の申し込み: {data['company_name']}"
        message = f"企業名: {data['company_name']}\n担当者: {data['contact_name']}\nEmail: {data['email']}\nTel: {data['phone']}\n住所: {data['address']}"
        
        superuser_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
        if superuser_emails:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, superuser_emails, fail_silently=False)

        return super().form_valid(form)