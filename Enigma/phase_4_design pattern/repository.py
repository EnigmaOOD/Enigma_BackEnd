"""
Doc URL:
https://docs.google.com/document/d/1HzExkOfn7xCqBZCMLCe_pMLXs_cgwBewa0VUgncI2-8/edit
"""
# buy_repository.py
from .models import Buy

class BuyRepository:
    def create(self, data):
        buy = Buy(**data)
        buy.save()
        return buy

    def retrieve(self, buy_id):
        return Buy.objects.get(id=buy_id)

    def update(self, buy_id, data):
        buy = self.retrieve(buy_id)
        for key, value in data.items():
            setattr(buy, key, value)
        buy.save()
        return buy

    def delete(self, buy_id):
        buy = self.retrieve(buy_id)
        buy.delete()


# buyer_repository.py
from .models import Buyer

class BuyerRepository:
    def create(self, data):
        buyer = Buyer(**data)
        buyer.save()
        return buyer

    def retrieve(self, buyer_id):
        return Buyer.objects.get(id=buyer_id)

    def update(self, buyer_id, data):
        buyer = self.retrieve(buyer_id)
        for key, value in data.items():
            setattr(buyer, key, value)
        buyer.save()
        return buyer

    def delete(self, buyer_id):
        buyer = self.retrieve(buyer_id)
        buyer.delete()


# consumer_repository.py
from .models import Consumer

class ConsumerRepository:
    def create(self, data):
        consumer = Consumer(**data)
        consumer.save()
        return consumer

    def retrieve(self, consumer_id):
        return Consumer.objects.get(id=consumer_id)

    def update(self, consumer_id, data):
        consumer = self.retrieve(consumer_id)
        for key, value in data.items():
            setattr(consumer, key, value)
        consumer.save()
        return consumer

    def delete(self, consumer_id):
        consumer = self.retrieve(consumer_id)
        consumer.delete()
## Example: create buy after defining repository

from .models import buy, buyer, consumer
from .repositories import BuyRepository, BuyerRepository, ConsumerRepository

class CreateBuySerializer(serializers.ModelSerializer):
    buyers = BuyerSerializer(many=True)
    consumers = ConsumerSerializer(many=True)

    class Meta:
        model = buy
        fields = "__all__"

    def create(self, validated_data):
        buyers_data = validated_data.pop('buyers')
        consumers_data = validated_data.pop('consumers')

        buy_repository = BuyRepository()  # ایجاد نمونه از مخزن BuyRepository
        buyer_repository = BuyerRepository()
        consumer_repository = ConsumerRepository()

        buy_instance = buy_repository.create(**validated_data)

        for buyer_data in buyers_data:
            buyer_instance = buyer_repository.objects.create(
                buy=buy_instance, **buyer_data)

        for consumer_data in consumers_data:
            consumer_instance = consumer_repository.objects.create(
                buy=buy_instance, **consumer_data)

        return buy_instance
