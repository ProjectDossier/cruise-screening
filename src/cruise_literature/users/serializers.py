from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model() 

class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(
        required=False,
        help_text=(
            "It is not required but it is the only way to recover your password if you forget it. "
            "You will be able to add it later."
        )
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

    def validate(self, data):
        # Check that the two passwords match
        if data.get('password1') != data.get('password2'):
            raise serializers.ValidationError({"password2": "Passwords must match."})
        return data

    def create(self, validated_data):
        # Remove password1 and password2 from the validated data
        password = validated_data.pop('password1')
        validated_data.pop('password2')
        
        # Create the user
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

