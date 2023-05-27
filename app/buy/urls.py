from django.urls import path
from . import views

app_name = 'buy'
urlpatterns = [

    path('GetGroupBuys/', views.GetGroupBuys.as_view(), name='GetGroupBuys'),
    path('UserGroupBuys/', views.UserGroupBuys.as_view(), name='UserGroupBuys'),
    path('CreateBuyView/', views.CreateBuyView.as_view(), name='CreateBuyView'),

]