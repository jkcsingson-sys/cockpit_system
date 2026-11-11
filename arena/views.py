from django.shortcuts import render

# Create your views here.
import base64
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render
from .forms import TransactionForm
from .models import Event, Transaction


@login_required
def entry_view(request):
  active_event = Event.objects.filter(is_active=True).first()
  if not active_event:
    messages.error(
        request, 'No active event found. Please create or activate an event.'
    )

  if request.method == 'POST':
    form = TransactionForm(request.POST, request.FILES)
    if form.is_valid():
      transaction = form.save(commit=False)
      transaction.event = active_event
      transaction.it_user = request.user

      # Handle Base64 signature from HTML5 Canvas
      sig_data = form.cleaned_data.get('signature_data')
      if sig_data and 'base64,' in sig_data:
        format_str, imgstr = sig_data.split(';base64,')
        ext = format_str.split('/')[-1]
        transaction.signature.save(
            f'sig_{request.user.id}_{transaction.fight_number}.{ext}',
            ContentFile(base64.b64decode(imgstr)),
            save=False,
        )

      transaction.save()
      messages.success(
          request,
          f'Successfully logged {transaction.get_transaction_type_display()} for'
          f' {transaction.teller.name}!',
      )
      return redirect('entry')
  else:
    form = TransactionForm()

  recent_transactions = (
      Transaction.objects.filter(event=active_event).order_by('-timestamp')[:10]
      if active_event
      else []
  )

  return render(
      request,
      'arena/entry.html',
      {
          'form': form,
          'active_event': active_event,
          'recent_transactions': recent_transactions,
      },
  )