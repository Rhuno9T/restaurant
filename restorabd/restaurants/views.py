from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from .models import Restaurant, ServiceTime, RestaurantReview, Order
from reviews.models import Review
from general.functions import getReviewStatus
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from notifications.models import Notification


def restauranJson_view(request):
    '''restaurants = Restaurant.objects.all().filter(is_active=True)
    data        = serializers.serialize('json', restaurants)
    return HttpResponse(data, content_type='application/json')'''
    #return JsonResponse(restaurants)
    r = Notification.objects.first()
    return render(request, 'test.html', {'r': r})

def restaurant_list(request):
    template_name = 'restaurants/restaurants_list.html'
    if request.is_ajax() and request.method == "POST":
        request_data = int(request.POST['dataNo'])
        restaurants = Restaurant.objects.all().filter(is_active=True)[request_data:(request_data+10)]
        return render(request, 'restaurants/load_more_restaurant.html', {'restaurants': restaurants})
    restaurants   = Restaurant.objects.all().filter(is_active=True)[:20]
    contex        = {
        'restaurants': restaurants
    }

    return render(request, template_name, contex)

def restaurant_detail(request, slug):
    try:
        restaurant = Restaurant.objects.get(slug=slug)
    except Restaurant.DoesNotExist:
        return HttpResponseRedirect("/404notfound/")

    service_times = ServiceTime.objects.get(restaurant=restaurant)
    review = RestaurantReview.objects.all().filter(restaurant=restaurant)

    # Get sales report, best selling item, and least selling item
    # sales_report = Order.objects.filter(restaurant=restaurant).values('items__name').annotate(total_sales=Count('items')).order_by('-total_sales')
    # best_selling_item = Order.objects.filter(restaurant=restaurant).values('items__name').annotate(total_sales=Count('items')).order_by('-total_sales').first()
    # least_selling_item = Order.objects.filter(restaurant=restaurant).values('items__name').annotate(total_sales=Count('items')).order_by('total_sales').first()

    template_name = 'restaurants/detail.html'
    context = {
        'restaurant': restaurant,
        'service_times': service_times,
        'active_d': 'tab_a_active',
        'foods': restaurant.food_items.all(),
        'review': review,
        # 'sales_report': sales_report,
        # 'best_selling_item': best_selling_item['items__name'] if best_selling_item else None,
        # 'least_selling_item': least_selling_item['items__name'] if least_selling_item else None,
    }

    return render(request, template_name, context)


def restaurant_review(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    template_name = 'restaurants/review.html'
    review = RestaurantReview.objects.get(restaurant=restaurant)
    service_times = ServiceTime.objects.get(restaurant=restaurant)
    food = getReviewStatus(review.food)
    price = getReviewStatus(review.price)
    service = getReviewStatus(review.service)
    environment = getReviewStatus(review.environment)
    user_reviews = Review.objects.all().filter(restaurant=restaurant)
    
    # Get sales report, best selling item, and least selling item
    sales_report = restaurant.get_sales_report()
    best_selling_item = restaurant.get_best_selling_item()
    least_selling_item = restaurant.get_least_selling_item()
    
    context = {
        'review': review,
        'restaurant': restaurant,
        'active_r': 'tab_a_active',
        'service_times': service_times,
        'user_reviews': user_reviews,
        'food': food,
        'service': service,
        'price': price,
        'environment': environment,
        'sales_report': sales_report,
        'best_selling_item': best_selling_item,
        'least_selling_item': least_selling_item,
    }

    return render(request, template_name, context)

def preorder(request):
    return render(request, 'pre-order.html')
