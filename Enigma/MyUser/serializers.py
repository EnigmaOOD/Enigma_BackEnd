from .models import MyUser

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotAcceptable
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.password_validation import validate_password

class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("email", "password", "user_id","name", "picture_id")
    

    user_id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(max_length=50, required=True)
    picture_id = serializers.IntegerField(required=True)

   
    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user
    def validate(self, data):
        if data['picture_id'] > 21:
                raise serializers.ValidationError(
                    f"picture_id should be less than 12")
        return data
    def validate_email(self, value):
        if get_user_model().objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("email exists.")
        return value

# class ChangePasswordSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, required=True)
#     old_password = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = get_user_model()
#         fields = ('old_password', 'password', 'password2')

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})

#         return attrs

#     def validate_old_password(self, value):
#         user = self.context['request'].user
#         if not user.check_password(value):
#             raise serializers.ValidationError({"old_password": "Old password is not correct"})
#         return value

#     def update(self, instance, validated_data):

#         instance.set_password(validated_data['password'])
#         instance.save()

#         return instance
    

class UpdateUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = MyUser
        fields = ("name", "picture_id")
        partial = True

    def validate(self, data):
        # Check that at least one of 'name' or 'picture_id' is present in request data
        if 'name' not in data and 'picture_id' not in data:
            raise serializers.ValidationError('Either name or picture_id must be provided')

        return data

