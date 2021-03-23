from user.models import User
from django.conf import settings
import jwt


class Token:
    def get_token(username):
        user = User.objects.get(username=username)

        if user:
            auth_token = jwt.encode(
                {'username': user.username}, settings.SECRET_KEY, algorithm='HS256')

            return auth_token
