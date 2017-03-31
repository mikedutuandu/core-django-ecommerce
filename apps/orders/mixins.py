from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from apps.carts.models import Cart
from .models import Order
from apps.carts.mixins import TokenMixin
from .models import UserAddress, UserCheckout, Order
from django.contrib.auth import get_user_model
User = get_user_model()


class LoginRequiredMixin(object):
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(LoginRequiredMixin, self).dispatch(request,*args, **kwargs)



class CartOrderMixin(object):
	def get_order(self, *args, **kwargs):
		cart = self.get_cart()
		if cart is None:
			return None
		new_order_id = self.request.session.get("order_id")
		if new_order_id is None:
			new_order = Order.objects.create(cart=cart)
			self.request.session["order_id"] = new_order.id
		else:
			new_order = Order.objects.get(id=new_order_id)
		return new_order

	def get_cart(self, *args, **kwargs):
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			return None
		cart = Cart.objects.get(id=cart_id)
		if cart.items.count() <= 0:
			return None
		return cart


class UserCheckoutMixin(TokenMixin, object):
	def user_failure(self, message=None):
		data = {
			"message": "There was an error. Please try again.",
			"success": False
		}
		if message:
			data["message"] = message
		return data

	def get_checkout_data(self, user=None, email=None):
		if email and not user:
			user_exists = User.objects.filter(email=email).count()
			if user_exists != 0:
				return self.user_failure(message="This user already exists, please login.")

		data = {}
		user_checkout = None
		if user and not email:
			if user.is_authenticated():
				user_checkout = UserCheckout.objects.get_or_create(user=user, email=user.email)[
					0]  # (instance, created)

		elif email:
			try:
				user_checkout = UserCheckout.objects.get_or_create(email=email)[0]
				if user:
					user_checkout.user = user
					user_checkout.save()
			except:
				pass  # (instance, created)
		else:
			pass

		if user_checkout:
			data["success"] = True
			data["braintree_id"] = user_checkout.get_braintree_id
			data["user_checkout_id"] = user_checkout.id
			data["user_checkout_token"] = self.create_token(data)

			del data["braintree_id"]
			del data["user_checkout_id"]
			data["braintree_client_token"] = user_checkout.get_client_token()

		return data