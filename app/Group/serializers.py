from rest_framework import serializers
from .models import MyUser, Group, Members


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('user_id', 'email', 'name', 'picture_id')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    groupID = GroupSerializer(read_only=True)
    userID = MyUserSerializer(read_only=True)

    class Meta:
        model = Members
        fields = "__all__"

    def create(self, validated_data):
        new_group = Group.objects.create(**validated_data)
        return new_group


class ShowMemberSerializer(serializers.ModelSerializer):
    userID = MyUserSerializer(read_only=True)

    class Meta:
        model = Members
        fields = ['id', 'userID']


# Add_user Should change the name
# class MembersSerializer(serializers.Serializer):
#     emails = serializers.ListField(child=serializers.EmailField())
#     groupID = serializers.IntegerField()


class AmountDebtandCreditMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Members
        fields = "__all__"
