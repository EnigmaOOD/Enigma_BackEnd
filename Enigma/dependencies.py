import importlib
from Enigma import settings

cache_servise_class_neme = settings.Cache_Redis_SERVICE
cache_servise_class = getattr(importlib.import_module(cache_servise_class_neme.rsplit('.', 1)[0]), cache_servise_class_neme.rsplit('.', 1)[1])
cache_servise_instance = cache_servise_class()

debtandcredit_calculate_servise_class_neme = settings.Debt_And_Credit_Calculate_SERVICE
debtandcredit_calculate_servise_class = getattr(importlib.import_module(debtandcredit_calculate_servise_class_neme.rsplit('.', 1)[0]), debtandcredit_calculate_servise_class_neme.rsplit('.', 1)[1])
debtandcredit_calculate_servise_instance = debtandcredit_calculate_servise_class()