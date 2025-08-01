from django.shortcuts import render, get_object_or_404,redirect
from .models import Article,PaidOrder,Order
from .templatetags.split_text import split_paragraphs_into_boxes
import stripe
from django.views import View
from django.http import JsonResponse
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, 'index.html')  # Отдаём шаблон index.html

def article_detail(request, title):
    article = get_object_or_404(Article, title__iexact=title)
    processed_content = split_paragraphs_into_boxes(article.content, max_chars=400)
    return render(request, "index.html", {
        "article": article,
        "processed_content": processed_content
    })

def search_articles(request):
    query = request.GET.get('q', '')
    if query:
        results = Article.objects.filter(title__icontains=query)
        if results.count() == 0:
            # Если статья не найдена, перенаправляем на главную страницу
            return redirect('articles:home')
        elif results.count() == 1:
            # Если найдена ровно одна статья, перенаправляем на её страницу
            article = results.first()
            return redirect('articles:article_detail', title=article.title)
        else:
            # Если найдено несколько, отображаем результаты поиска
            context = {
                'query': query,
                'results': results,
            }
            return render(request, "articles/search_results.html", context)
    else:
        # Если запрос пустой, перенаправляем на главную
        return redirect('articles:home')


def create_donation_session(request):
    # Укажите сумму в центах (например, 500 = $5.00)
    donation_amount = 100

    # Создаем сессию Checkout
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Donation',
                },
                'unit_amount': donation_amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/donation/success/'),
        cancel_url=request.build_absolute_uri('/donation/cancel/'),
    )

    return redirect(session.url, code=303)

class donation_success(View):
    def get(self, request):
        return render(request, 'donation_success.html')

class donation_cancel(View):
    def get(self, request):
        return render(request, 'donation_cancel.html')

def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Проверяем событие оплаты
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')

        if order_id:
            order = Order.objects.get(id=order_id)
            for item in order.basket_set.all():
                PaidOrder.objects.create(
                    user=order.user,
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.sum(),
                    stripe_session_id=session['id']
                )

            # Удаляем корзину после оплаты
            order.basket_set.all().delete()

    return JsonResponse({'status': 'success'}, status=200)
