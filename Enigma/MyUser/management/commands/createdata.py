import random
from Group.models import Group, Members
import faker.providers
from django.core.management.base import BaseCommand
from faker import Faker
import faker.providers
from MyUser.models import MyUser
from fake_persian_name import fake_name as fpn
from buy.models import buy,buyer,consumer


Products =["پیتزا", 
"فلافل", 
"رزرو هتل", 
"کباب",
 "جوجه کباب",
 "بستنی", 
 "بلیط هواپیما", 
 "پرداخت هزینه اسنپ", 
 "دوغ و گوشفیل", 
 "قهوه", 
 "کیک و نوشابه", 
 "کیک و شیر کاکائو", 
 "بلیط موزه", 
 "بلیط سینما", 
 "بلیط شهربازی",
 "اجاره خونه",
 "مواد غذایی برای خرید غذا",
 "کیک تولد",
 "کافه"
]

GroupNames =[
    "شمال با دوستان",
    "دوستان قدیمی",
    "خاندان احتشام",
    "دور ایران در 72 روز",
    "تولد سوپرایز",
    "اصفهان گردی",
    "سفر کاری برای پروژه",
    "یزد گردی",
    "اردوی کیش"
]
PersonNames =[
    " فاطمه",
    "نوریه",
    "زهرا",
    "مریم",
    "محمد",
    "رضا",
    "امیر", 
    "حسین",
    "فرزان",
    "مسعود",
    "نسیم",
    "نیلوفر",
    "نسترن",
    "محمد جواد",
    "علی"
]
class Provider(faker.providers.BaseProvider):
    def groupnames(self):
        return self.random_element(GroupNames)

    def products(self):
        return self.random_element(Products) 
    
    def personnames(self):
        return self.random_element(PersonNames)


class Command(BaseCommand):
    help = "Command information"

    def handle(self, *args, **kwargs):

        fake = Faker()
        fake.add_provider(Provider)
        user_list = []
        group_list = []

        # genetate user
        for i in range(1000):
            name = fake.personnames()
            password = fake.password()
            email = fake.unique.email()
            user = MyUser.objects.create(email=email, name=name,password=password, picture_id=random.randrange(0, 21))
            print(type(user))
            user_list.append(user)
        

        # generate group

        for _ in range(5000):
            gname = fake.groupnames()
            description = fake.groupnames()
            currency = fake.currency_name()
            group = Group.objects.create(name=gname,description=description,currency=currency,picture_id=random.randrange(0, 3))
            for _ in range(random.randrange(2, 5)):
                Members.objects.create(userID=random.choice(user_list), groupID=group)
            group_list.append(group)
        
        
        # create buy
        for i in range(1000):
            print("creating buyer")
            description = fake.products()
            cost = random.randrange(10000, 1000000000)
            date = fake.date()
            groupID = random.choice(group_list)
            members_list = Members.objects.filter(groupID=groupID)
            Buy = buy.objects.create(description=description, cost=cost, groupID=groupID, added_by=random.choice(members_list).userID, date=date, picture_id=random.randrange(0, 35))
            buyers_number = random.randrange(1, len(members_list))
            consumer_number = random.randrange(1, len(members_list))
            for i in range(buyers_number):
                buyer.objects.create(buy=Buy, userID=members_list[i].userID, percent=cost/buyers_number)
            for i in range(consumer_number):
                consumer.objects.create(buy=Buy, userID=members_list[i].userID, percent=cost/consumer_number)

        return   
