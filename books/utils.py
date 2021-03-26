from django.core.mail import EmailMessage
import logging
from user.models import User
from datetime import datetime, timedelta
from psycopg2 import OperationalError
from .models import Order
from rest_framework.exceptions import ValidationError
from celery import shared_task

logger = logging.getLogger('django')


class Util:
    @shared_task
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()

    @shared_task
    def send_delivery_email(email):
        try:
            order = Order.objects.filter(is_delivered=False)
            if order:
                order_list = order.values('id')
                for orders in range(len(order_list)):
                    order_id = order_list[orders]['id']
                    order_obj = Order.objects.get(id=order_id)
                    user = User.objects.get(id=order_obj.owner_id)
                    orderd_time = order_obj.created_date
                    if datetime.now() - orderd_time.replace(tzinfo=None) > timedelta(hours=24):
                        email_body = 'Hi ' + user.username + \
                                     ' your order has been delivered successully'
                        data = {'email_body': email_body, 'to_email': user.email,
                                'email_subject': 'Order Delivered'}
                        Util.send_email(data)
                        order_obj.is_delivered = True
                        order_obj.save()
                        logger.info("Email sent successfully using celery")

        except OperationalError as e:
            logger.error(e)
        except ValidationError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
            print(e)
