import importlib
from Enigma import settings

cache_servise_class_neme = settings.Cache_Redis_SERVICE
cache_servise_class = getattr(importlib.import_module(cache_servise_class_neme.rsplit('.', 1)[0]), cache_servise_class_neme.rsplit('.', 1)[1])
cache_servise_instance = cache_servise_class()

debtandcredit_calculate_servise_class_neme = settings.Debt_And_Credit_Calculate_SERVICE
debtandcredit_calculate_servise_class = getattr(importlib.import_module(debtandcredit_calculate_servise_class_neme.rsplit('.', 1)[0]), debtandcredit_calculate_servise_class_neme.rsplit('.', 1)[1])
debtandcredit_calculate_servise_instance = debtandcredit_calculate_servise_class()

filter_servise_class_neme = settings.Filter_SERVICE
filter_servise_class = getattr(importlib.import_module(filter_servise_class_neme.rsplit('.', 1)[0]), filter_servise_class_neme.rsplit('.', 1)[1])
filter_servise_instance = filter_servise_class()

cost_calculate_servise_class_neme = settings.Calculate_Cost_Service
cost_calculate_servise_class = getattr(importlib.import_module(cost_calculate_servise_class_neme.rsplit('.', 1)[0]), cost_calculate_servise_class_neme.rsplit('.', 1)[1])
cost_calculate_servise_instance = cost_calculate_servise_class()

user_group_servise_class_neme = settings.User_Group_SERVICE
user_group_servise_class = getattr(importlib.import_module(user_group_servise_class_neme.rsplit('.', 1)[0]), user_group_servise_class_neme.rsplit('.', 1)[1])
user_group_servise_instance = user_group_servise_class()