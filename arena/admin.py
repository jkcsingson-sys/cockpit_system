from django.urls import path
from django.contrib import admin
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
        'fight_number',
        'teller',
        'transaction_type',
        'amount',
        'it_user',
        'timestamp',
    )
    list_filter = ('transaction_type', 'event', 'timestamp')
    search_fields = ('teller__name', 'it_user__username', 'fight_number')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('print-report/', self.admin_site.admin_view(self.print_report_view), name='transaction-print-report'),
        ]
        return custom_urls + urls

    def print_report_view(self, request):
        from django.shortcuts import render
        from django.db.models import Sum

        transactions = Transaction.objects.all()
        total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0

        context = {
            'transactions': transactions,
            'total_amount': total_amount,
            'title': 'Post-Fight Transaction Summary Report',
        }
        return render(request, 'admin/arena/transaction/print_report.html', context)