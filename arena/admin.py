from django.contrib import admin
from django.urls import path
from django.db.models import Sum
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms import ModelForm
from .models import Event, Teller, Transaction

# Override Admin site titles
admin.site.site_header = "Admin"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Cockpit System Administration"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'is_active', 'created_at')
    list_filter = ('is_active', 'date')
    search_fields = ('name',)


@admin.register(Teller)
class TellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


class TransactionAdminForm(ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.signature:
                sig_html = f'<br/><img src="{self.instance.signature.url}" style="max-height: 100px; border: 1px solid #ccc; border-radius: 4px; background: #fff; padding: 4px; margin-top: 8px;" />'
                self.fields['signature'].help_text = mark_safe(sig_html)
            
            if self.instance.photo:
                photo_html = f'<br/><img src="{self.instance.photo.url}" style="max-height: 160px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); margin-top: 8px;" />'
                self.fields['photo'].help_text = mark_safe(photo_html)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionAdminForm
    change_list_template = "admin/arena/transaction/change_list.html"

    list_display = (
        'teller',              
        'transaction_type',    
        'amount',              
        'it_user',             
        'timestamp',           
        'event',               
    )
    list_filter = ('teller', 'transaction_type', 'event', 'timestamp')
    search_fields = ('teller__name', 'it_user__username')
    
    readonly_fields = ('timestamp', 'it_user')

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        
        qs = response.context_data['cl'].queryset
        
        total_amount = 0
        for txn in qs:
            t_type = str(getattr(txn, 'transaction_type', '')).lower()
            try:
                t_display = str(txn.get_transaction_type_display()).lower()
            except (AttributeError, TypeError):
                t_display = t_type
            
            amount = float(getattr(txn, 'amount', 0) or 0)
            
            if 'partial' in t_type or 'partial' in t_display:
                total_amount += amount
            elif 'request' in t_type or 'request' in t_display:
                total_amount -= amount
        
        if extra_context is None:
            extra_context = {}
        extra_context['total_amount'] = total_amount
        response.context_data.update(extra_context)
            
        return response

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('print-report/', self.admin_site.admin_view(self.print_report_view), name='transaction-print-report'),
        ]
        return custom_urls + urls

    def print_report_view(self, request):
        from django.shortcuts import render
        active_event = Event.objects.filter(is_active=True).first()
        if active_event:
            transactions = Transaction.objects.filter(event=active_event)
        else:
            transactions = Transaction.objects.none()

        total_amount = 0
        for txn in transactions:
            t_type = str(getattr(txn, 'transaction_type', '')).lower()
            try:
                t_display = str(txn.get_transaction_type_display()).lower()
            except (AttributeError, TypeError):
                t_display = t_type
                
            amount = float(getattr(txn, 'amount', 0) or 0)
            
            if 'partial' in t_type or 'partial' in t_display:
                total_amount += amount
            elif 'request' in t_type or 'request' in t_display:
                total_amount -= amount

        context = {
            'transactions': transactions,
            'total_amount': total_amount,
            'active_event': active_event,
            'title': f'Post-Fight Transaction Summary Report - {active_event.name if active_event else "No Active Event"}',
        }
        return render(request, 'admin/arena/transaction/print_report.html', context)