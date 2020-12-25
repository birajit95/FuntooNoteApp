from django.core.mail import EmailMessage


class Email:
    @staticmethod
    def configureEmail(token, user, current_site, relative_url):
        absoluteURL = "http://"+current_site+'/'+relative_url+"?token="+str(token)
        email_body = f"Hi {user.username}! use the link bellow to verify your email \n {absoluteURL}"
        email_data = {'email_body': email_body, 'email_subject': 'Verify your email', 'to_email': user.email}
        return email_data

    @staticmethod
    def sendEmail(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=(data['to_email'],)
          )
        email.send()
