from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate
from .error_codes import ErrorCodes
from .models import User


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    email = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)

    def validate(self, data):
        ec = ErrorCodes()
        username = data.get("username", "")
        email = data.get("email", "")
        password = data.get("password", "")

        if username and email and password:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            user.save()
            if user:
                if user.is_active:
                    data["user"] = user
                    data["user_id"] = user.id
                else:
                    raise exceptions.ValidationError(ec.account_deactivated)
            else:
                raise exceptions.ValidationError(ec.signup_failed)
        else:
            raise exceptions.ValidationError(ec.required_credenials_signup)
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=100)

    def validate(self, params):
        ec = ErrorCodes()
        username = params.get("username", "")
        password = params.get("password", "")

        if username and password:
            user: User = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    params["user"] = user
                    params["user_id"] = user.id
                else:
                    raise exceptions.ValidationError(ec.account_deactivated)
            else:
                raise exceptions.ValidationError(ec.wrong_credentials)
        else:
            raise exceptions.ValidationError(ec.required_credenials)
        return params
