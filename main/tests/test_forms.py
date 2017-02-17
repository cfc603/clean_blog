from django.conf import settings
from django.core import mail
from django.test import TestCase

from main.forms import ContactForm


class ContactFormTest(TestCase):

    def valid_contact_form_send_confirmation(self):
        data = {
            'name': 'Jimmy Test',
            'email': 'jt@test.com',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=data)
        form.is_valid()
        form.send_confirmation()

    def valid_contact_form_send_email(self):
        data = {
            'name': 'Jimmy Test',
            'email': 'jt@test.com',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=data)
        form.is_valid()
        form.send_email()

    def test_send_confirmation_outbox_count_one(self):
        self.valid_contact_form_send_confirmation()
        self.assertEqual(len(mail.outbox), 1)

    def test_send_confirmation_expected_subject(self):
        self.valid_contact_form_send_confirmation()
        self.assertEqual(mail.outbox[0].subject, 'Your message has been sent.')

    def test_send_confirmation_expected_body(self):
        self.valid_contact_form_send_confirmation()
        body = mail.outbox[0].body
        self.assertIn('Jimmy Test', body)

    def test_send_confirmation_expected_from_email(self):
        self.valid_contact_form_send_confirmation()
        self.assertEqual(settings.SERVER_EMAIL, mail.outbox[0].from_email)

    def test_send_confirmation_expected_to_email(self):
        self.valid_contact_form_send_confirmation()
        to_list = mail.outbox[0].to
        self.assertEqual(1, len(to_list))
        self.assertEqual('jt@test.com', to_list[0])

    def test_send_email_outbox_count_one(self):
        self.valid_contact_form_send_email()
        self.assertEqual(len(mail.outbox), 1)

    def test_send_email_expected_subject(self):
        self.valid_contact_form_send_email()
        self.assertEqual(mail.outbox[0].subject, 'Contact Form Submission')

    def test_send_email_expected_body(self):
        self.valid_contact_form_send_email()
        body = mail.outbox[0].body
        self.assertIn('Jimmy Test', body)
        self.assertIn('jt@test.com', body)
        self.assertIn('This is a test message.', body)

    def test_send_email_expected_from_email(self):
        self.valid_contact_form_send_email()
        self.assertEqual(settings.SERVER_EMAIL, mail.outbox[0].from_email)

    def test_send_email_expected_to_email(self):
        self.valid_contact_form_send_email()
        to_list = mail.outbox[0].to
        self.assertEqual(1, len(to_list))
        self.assertEqual(settings.SERVER_EMAIL, to_list[0])

    def test_send_email_expected_reply_to(self):
        self.valid_contact_form_send_email()
        reply_to_list = mail.outbox[0].reply_to
        self.assertEqual(1, len(reply_to_list))
        self.assertEqual('jt@test.com', reply_to_list[0])
