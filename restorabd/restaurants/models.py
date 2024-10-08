from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import pre_save, post_save
from general.functions import *
from foods.models import Food
from informations.models import City
from django.db.models import Count

class RestaurantManager(models.Manager):
    def all(self):
        return self.filter(is_active=True)

from django.db import models
from cryptography.fernet import Fernet
import base64

# Key should be securely stored and loaded as shown previously
key = Fernet.generate_key()
cipher_suite = Fernet(key)

class EncryptedField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 255)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
    
        try:
            # Check if the value is encrypted (e.g., base64 encoded string)
            decoded_value = base64.urlsafe_b64decode(value + '=' * (-len(value) % 4))
            decrypted_value = cipher_suite.decrypt(decoded_value).decode('utf-8')
            return decrypted_value
        except (TypeError, ValueError):
            # If decryption fails, return the value as-is
            return value


    def get_prep_value(self, value):
        if value is None:
            return value
        
        # Encrypt and encode the value with correct padding
        try:
            encrypted_value = cipher_suite.encrypt(value.encode('utf-8'))
            encoded_value = base64.urlsafe_b64encode(encrypted_value).decode('utf-8')
            return encoded_value.rstrip('=')  # Remove padding
        except Exception as e:
            # Handle encryption errors
            raise ValueError(f"Encryption error: {e}")




class Restaurant(models.Model):
    # Basic
    title = models.CharField(max_length=500, blank=False, null=False)
    slug = models.SlugField(blank=True, unique=True)
    phone = EncryptedField(max_length=128, blank=False, null=False)
    email = EncryptedField(max_length=252, blank=True, null=True, default='')
    
    # Minimum
    min_serve_time = models.IntegerField(default=30, blank=False, verbose_name='Minimum Serve Time')
    min_order_tk = models.FloatField(default=150.00, blank=False, verbose_name='Minimum Order')
    service_charge = models.FloatField(default=30.00, blank=False, verbose_name='Service Charge')
    vat_tax = models.FloatField(default=0.0, blank=True, verbose_name='Vat/Tax')
    
    # Location/Contact
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address = EncryptedField(max_length=1024, blank=False, null=False)
    environment = EncryptedField(max_length=512, blank=False, null=False)
    map_embed_url = EncryptedField(blank=False, default='https://maps.google.com/')
    
    # Photos
    logo = models.ImageField(
        'logo',
        upload_to="restaurant_logo/",
        null=True, blank=True,
        width_field="logo_width_field",
        height_field="logo_height_field",
    )
    logo_height_field = models.IntegerField(default=0)
    logo_width_field = models.IntegerField(default=0)
    pp = models.ImageField(
        'profile photo',
        upload_to="restaurant_pp/",
        null=True, blank=True,
        width_field="pp_width_field",
        height_field="pp_height_field",
    )
    pp_height_field = models.IntegerField(default=0)
    pp_width_field = models.IntegerField(default=0)
    
    # Others
    is_active = models.BooleanField(default=False)
    is_orderable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_info = models.TextField(blank=True, null=True)
    food_items = models.ManyToManyField(Food, blank=True)
    
    # Restaurant qs manager
    objects = RestaurantManager()

    def __str__(self):
        return self.title + " - " + self.slug

    def get_absolute_url(self):
        return reverse("restaurants:detail", kwargs={"slug": self.slug})

    def get_review_page_url(self):
        return reverse("restaurants:review", kwargs={"slug": self.slug})
    
    def get_sales_report(self):
        sales_report = self.order_set.values('items__name').annotate(total_sales=Count('items')).order_by('-total_sales')
        return sales_report

    def get_best_selling_item(self):
        best_selling_item = self.order_set.values('items__name').annotate(total_sales=Count('items')).order_by('-total_sales').first()
        if best_selling_item:
            return best_selling_item['items__name']
        return None

    def get_least_selling_item(self):
        least_selling_item = self.order_set.values('items__name').annotate(total_sales=Count('items')).order_by('total_sales').first()
        if least_selling_item:
            return least_selling_item['items__name']
        return None

    class Meta:
        ordering = ['-created_at']


class Order(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

class RestaurantReview(models.Model):
    restaurant         = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    food               = models.FloatField(default=0.0, blank=True)
    price              = models.FloatField(default=0.0, blank=True)
    service            = models.FloatField(default=0.0, blank=True)
    environment        = models.FloatField(default=0.0, blank=True)
    reviewed_people_no = models.IntegerField(default=0, blank=True)
    average            = models.FloatField(default=0.00, blank=True)
    status             = models.CharField(max_length=50, default='N/A', blank=True, null=True)    
    star1              = models.CharField(max_length=50, default='fa-star-o text-secondary')
    star2              = models.CharField(max_length=50, default='fa-star-o text-secondary')
    star3              = models.CharField(max_length=50, default='fa-star-o text-secondary')
    star4              = models.CharField(max_length=50, default='fa-star-o text-secondary')
    star5              = models.CharField(max_length=50, default='fa-star-o text-secondary')

    created_at         = models.DateTimeField(auto_now=True)
    updated_at         = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.restaurant.title + ": " + self.status + " - " + str(self.average)





class ServiceTime(models.Model):
    restaurant         = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    open_at            = models.TimeField(blank=True, default='08:00:00')
    close_at           = models.TimeField(blank=True, default='20:00:00')
    saturday           = models.BooleanField(default=True, blank=True)
    sunday             = models.BooleanField(default=True, blank=True)    
    monday             = models.BooleanField(default=True, blank=True)
    tuesday            = models.BooleanField(default=True, blank=True)
    wednesday          = models.BooleanField(default=True, blank=True)
    thursday           = models.BooleanField(default=True, blank=True)
    friday             = models.BooleanField(default=True, blank=True)
    created_at         = models.DateTimeField(auto_now=True)
    updated_at         = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.restaurant.title





def restaurant_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

def restaurant_post_save_receiver(sender, instance, *args, **kwargs):
    qs = RestaurantReview.objects.filter(restaurant=instance)
    if not qs.exists():    
        rr = RestaurantReview()
        rr.restaurant = instance
        rr.save()
    qs = ServiceTime.objects.filter(restaurant=instance)
    if not qs.exists():
        st = ServiceTime()
        st.restaurant = instance
        st.save()

pre_save.connect(restaurant_pre_save_receiver, sender=Restaurant)
post_save.connect(restaurant_post_save_receiver, sender=Restaurant)
