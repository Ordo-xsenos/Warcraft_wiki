from django.urls import path
from .views import home,article_detail,search_articles,create_donation_session,donation_success,donation_cancel,stripe_webhook

urlpatterns = [
    path('', home, name='home'),
    path('search/', search_articles, name='search_articles'),
    path('donation/', create_donation_session, name='create_donation_session'),
    path("<str:title>/", article_detail, name="article_detail"),
    path('donation/success/', donation_success.as_view(), name='donation_success'),
    path('donation/cancel/', donation_cancel.as_view(), name='donation_cancel'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]
