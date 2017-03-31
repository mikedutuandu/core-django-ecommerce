from django_filters import FilterSet, CharFilter, NumberFilter

from .models import Product

class ProductFilter(FilterSet):
	title = CharFilter(name='title', lookup_expr='icontains', distinct=True)
	category = CharFilter(name='categories__title', lookup_expr='icontains', distinct=True)
	category_id = CharFilter(name='categories__id', lookup_expr='icontains', distinct=True)
	min_price = NumberFilter(name='variation__price', lookup_expr='gte', distinct=True) # (some_price__gte=somequery)
	max_price = NumberFilter(name='variation__price', lookup_expr='lte', distinct=True)
	class Meta:
		model = Product
		fields = [
			'min_price',
			'max_price',
			'category',
			'title',
			'description',
		]