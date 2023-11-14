import requests

from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from collections import Counter
from geopy import distance
from environs import Env

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from foodcartapp.views import create_place
from place.models import Place


env = Env()
env.read_env()


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )
    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders_with_total_cost = []
    orders = Order.objects.get_orders()
    restaurant_menu_items = RestaurantMenuItem.objects.get_available_items()
    for order in orders:
        order_products = set(order.products.all().values_list('id', flat=True))
        available_restaurants = [item.restaurant for item in restaurant_menu_items.filter(product_id__in=order_products)]
        restaurant_counter = Counter(available_restaurants)
        selected_restaurants = [restaurant for restaurant, count in restaurant_counter.items() if count == len(order_products)]
        delivery_distance = []
        for restaurant in selected_restaurants:
            try:
                order_place = Place.objects.get(address=order.address)
                restaurant_place = Place.objects.get(address=restaurant.address)
                client_coordinates = [order_place.lat, order_place.lon]
                restaurant_coordinates = [restaurant_place.lat, restaurant_place.lon]
                distance_km = f'{round(distance.distance(client_coordinates, restaurant_coordinates).km, 2)} км'
                if not order_place.lat:
                    distance_km = 'Дистанция не определена'
                delivery_distance.append((restaurant.name, distance_km))
            except Place.DoesNotExist:
                create_place(order.address)
        order_payload = {
            'id': order.id,
            'status': order.get_status_display,
            'payment_method': order.get_payment_method_display,
            'cost': order.total_cost,
            'phone': order.phonenumber,
            'address': order.address,
            'comment': order.comment,
            'client': f'{order.firstname} {order.lastname}',
            'restaurant': order.restaurant,
            'distance': delivery_distance
        }
        orders_with_total_cost.append(order_payload)

    return render(request, template_name='order_items.html', context={
        'order_items': orders_with_total_cost,
    })

