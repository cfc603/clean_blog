from django import forms
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField(max_length=254, min_length=6)
    message = forms.CharField(widget=forms.Textarea)

    def send_confirmation(self):
        email = EmailMessage(
            subject='Your message has been sent.',
            body=render_to_string(
                'main/email/contact_confirmation.txt', 
                {'name': self.cleaned_data['name']}
            ),
            from_email=settings.SERVER_EMAIL,
            to=[self.cleaned_data['email'],]
        )
        email.send()

    def send_email(self):
        email = EmailMessage(
            subject='Contact Form Submission',
            body=render_to_string(
                'main/email/contact_form_email.txt', {
                    'name': self.cleaned_data['name'], 
                    'email': self.cleaned_data['email'], 
                    'message': self.cleaned_data['message']
                }
            ),
            from_email=settings.SERVER_EMAIL,
            to=[settings.SERVER_EMAIL,],
            reply_to=[self.cleaned_data['email']]
        )
        email.send()
