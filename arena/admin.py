from django.contrib import admin
from django.urls import path
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


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    change_list_template = "admin/arena/transaction/change_list.html"

    list_display = (
        'event',
        'teller',
        'transaction_type',
        'amount',
        'it_user',
        'timestamp',
    )
    list_filter = ('teller', 'transaction_type', 'event', 'timestamp')
    search_fields = ('teller__name', 'it_user__username')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('print-report/', self.admin_site.admin_view(self.print_report_view), name='transaction-print-report'),
        ]
        return custom_urls + urls

    def print_report_view(self, request):
        from django.shortcuts import render
        from django.db.models import Sum

        # Automatically grab the currently active event
        active_event = Event.objects.filter(is_active=True).first()
        
        if active_event:
            transactions = Transaction.objects.filter(event=active_event)
        else:
            transactions = Transaction.objects.none()

        total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0

        context = {
            'transactions': transactions,
            'total_amount': total_amount,
            'active_event': active_event,
            'title': f'Post-Fight Transaction Summary Report - {active_event.name if active_event else "No Active Event"}',
        }
        return render(request, 'admin/arena/transaction/print_report.html', context)