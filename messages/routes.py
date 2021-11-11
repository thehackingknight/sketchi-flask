
from flask import request, Blueprint
from .models import Message as M
from datetime import datetime
from flask_mail import Mail, Message
mail = Mail()
router = Blueprint('messages', __name__)

def send_email(subject, message, recipients, res=None):
    m = Message(
    subject= subject,
    sender="admin@tunedbass.com",
    recipients=recipients)
    
    m.html = message
    try:
        mail.send(m)
        return {"message" :'Email sent successfully'} if res is None else res
    except Exception as e:

        print(e)
        return {"message" : "Could not send email"}, 401

@router.post('/contact-us')
def contact():
    try:
        form = request.form
        msg = M()
        msg._from = {'name' :  form['name'], 'email' : form['email']}
        msg.body = form['message']
        msg.date_created = datetime.now()
        msg.save()

        message = f"""
                 <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style type="text/css">


                    .TunedBass{{
                        font: medium/ 1.5  Arial,Helvetica,sans-serif !important;
                        margin: auto;
                        padding: 10px;
                        color: black;

                    }}





                    .btn {{
                        cursor: pointer;
                        display: inline-block;
                        min-height: 1em;
                        outline: 0;
                        border: none;
                        vertical-align: baseline;
                        background: #e0e1e2 none;
                        color: rgba(0,0,0,.6);
                        font-family: Lato,"Helvetica Neue",Arial,Helvetica,sans-serif;
                        margin: 0 .25em 0 0;
                        padding: .78571429em 1.5em;
                        text-transform: none;
                        text-shadow: none;
                        font-weight: 600;
                        line-height: 1em;
                        font-style: normal;
                        text-align: center;
                        text-decoration: none;
                        border-radius: .28571429rem;
                        box-shadow: inset 0 0 0 1px transparent,inset 0 0 0 0 rgba(34,36,38,.15);
                        -webkit-user-select: none;
                        -ms-user-select: none;
                        user-select: none;
                        transition: opacity .1s ease,background-color .1s ease,color .1s ease,box-shadow .1s ease,background .1s ease;
                        will-change: "";
                        -webkit-tap-highlight-color: transparent;
                    }}
                    .btn-primary {{
                        color: #fff !important;
                        background-color: #0d6efd !important;
                        border-color: #0d6efd !important;

                    }}
            </style>
        </head>
        <body>

            <div class="TunedBass">

            <h1>TunedBass Contact us message.</h1>

            <div style="margin-top: 20px">
            <h3 style="margin-bottom: 10px; ">Sender details:</h3>
            <p><b>NAME: </b>{form['name']}</p>
            <p><b>EMAIL: </b>{form['email']}</p>
            </div>

            <p>{form['message']}</p>


        </body>
        </html>
                 """ 
        send_email('TunedBass contact us message', message, ['admin@tunedbass.com'])
        msg.sent = True
        msg.save()
        return 'Message sent', 200
    except Exception as e:
        print(e)
        return 'Something went wrong', 500