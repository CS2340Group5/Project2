from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from accounts.models import GenericUser
from .models import Message

# Create your views here.
@login_required
def send_email(request, id):
    applicant = get_object_or_404(GenericUser, id=id)

    if request.user.role == GenericUser.Role.RECRUITER:
        text = request.POST.get('message', '').strip()
        send_with = request.POST.get('method')
        if text:
            if send_with == 'email':
                if applicant.email:
                    send_mail(
                        f"New message from {request.user.username}",
                        f"{text}\n\n** Please note: This email is sent from an unattended mailbox. Replies will not be read **",
                        None,
                        [applicant.email]
                    )
            else:
                Message.objects.create(
                    recruiter=request.user,
                    applicant=applicant,
                    message_text=text
                )

    return redirect('accounts.profile_view', id=applicant.id)

@login_required
def sent_messages(request):
    template_data = {}
    template_data['sent_messages'] = list(request.user.recipient.order_by('-date'))
    request.user.recipient.filter(read=False).update(read=True)
    return render(request, 'messaging/receivedmessages.html', {'template_data': template_data})
