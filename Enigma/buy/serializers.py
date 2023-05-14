from rest_framework import serializers
from Group.models import Group, Members
from MyUser.models import MyUser
from .models import buy, buyer, consumer


class buyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = buyer
        fields = "__all__"

    def create(self, validated_data):
        new_buyer = buyer.objects.create(**validated_data)
        print(new_buyer)
        print("-------------------------------------------------")
        return new_buyer


class consumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = consumer
        fields = "__all__"

    def create(self, validated_data):
        new_consumer = consumer.objects.create(**validated_data)

        return new_consumer


"""
class buySerializer(serializers.ModelSerializer):
    class Meta:
        model = buy
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['username', 'picture_id']


# class BuyerSerializer(serializers.ModelSerializer): 
#     userID = MyUserSerializer()
"""


class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = buyer
        fields = ['userID', 'percent']

# class ConsumerSerializer(serializers.ModelSerializer):
#     userID = MyUserSerializer()


class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = consumer
        fields = ['userID', 'percent']


"""
class BuySerializer(serializers.ModelSerializer):
    Buyers = BuyerSerializer(many=True, read_only=True)
    consumers = ConsumerSerializer(many=True, read_only=True)

    class Meta:
        model = buyer
        fields = ['userID', 'percent']
"""


class CreateBuySerializer(serializers.ModelSerializer):
    buyers = BuyerSerializer(many=True)
    consumers = ConsumerSerializer(many=True)

    class Meta:
        model = buy
        fields = "__all__"

    def create(self, validated_data):
        buyers_data = validated_data.pop('buyers')
        consumers_data = validated_data.pop('consumers')

        buy_instance = buy.objects.create(**validated_data)

        for buyer_data in buyers_data:
            buyer_instance = buyer.objects.create(
                buy=buy_instance, **buyer_data)

        for consumer_data in consumers_data:
            consumer_instance = consumer.objects.create(
                buy=buy_instance, **consumer_data)
        return buy_instance

    def validate(self, data):
        print(self.initial_data)
        buyers_data = self.initial_data.get('buyers')
        consumers_data = self.initial_data.get('consumers')
        group_id = self.initial_data.get('groupID')
        total_buy = 0
        total_consume = 0
        for buyer in buyers_data:
            print(buyer)
            user_id = buyer['userID']
            print(user_id)
            member = Members.objects.filter(
                groupID_id=group_id, userID_id=user_id).exists()
            if not member:
                raise serializers.ValidationError(
                    f"Buyer with group ID {group_id} and user ID {user_id} is not a member of the group")
            if buyer['percent'] < 0:
                raise serializers.ValidationError(
                    f"Buyer with group ID {group_id} and user ID {user_id} should have positive value for percent!")
        for consumer in consumers_data:
            user_id = consumer['userID']
            member = Members.objects.filter(
                groupID_id=group_id, userID_id=user_id).exists()
            if not member:
                raise serializers.ValidationError(
                    f"Consumer with group ID {group_id} and user ID {user_id} is not a member of the group")
            if consumer['percent'] < 0:
                raise serializers.ValidationError(
                    f"Consumer with group ID {group_id} and user ID {user_id} should have positive value for percent!")

        return data


class BuyListSerializer(serializers.ModelSerializer):
    buyers = BuyerSerializer(many=True, required=False)
    consumers = ConsumerSerializer(many=True, required=False)

    class Meta:
        model = buy
        fields = "__all__"


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['user_id','name', 'picture_id']


class BuyerSerializer1(serializers.ModelSerializer):
    userID = MyUserSerializer()

    class Meta:
        model = buyer
        fields = ['userID', 'percent']


class ConsumerSerializer1(serializers.ModelSerializer):
    userID = MyUserSerializer()

    class Meta:
        model = consumer
        fields = ['userID', 'percent']


class BuySerializer(serializers.ModelSerializer):
    Buyers = BuyerSerializer1(many=True, read_only=True)
    consumers = ConsumerSerializer1(many=True, read_only=True)
    added_by = MyUserSerializer()

    class Meta:
        model = buy
        fields = ['id', 'cost', 'date','description', 'picture_id','added_by', 'Buyers', 'consumers']
