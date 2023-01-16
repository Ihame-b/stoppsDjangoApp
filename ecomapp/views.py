from django.views.generic import (
    View,
    TemplateView,
    CreateView,
    FormView,
    DetailView,
    ListView,
)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.urls import reverse
from django.core.paginator import Paginator
from .utils import password_reset_token
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q, Sum
from .models import (
    Admin,
    ProductOwner,
    Customer,
    Category,
    Product,
    ProductImage,
    Cart,
    Cargo,
    CartProduct,
    Order,
    LinfoxImage,
    ORDER_STATUS,
)
import requests

# import request
# from ecomproject.mixins import Directions

# from ecomproject.mixins import (
#     AjaxFormMixin,
#     reCAPTCHAValidation,
#     FormErrors,
#     RedirectParams,
# )
from .forms import (
    CheckoutForm,
    productOwnerRegistrationForm,
    CustomerRegistrationForm,
    CustomerLoginForm,
    PasswordForgotForm,
    PasswordResetForm,
    ProductForm,
    CargoForm,
    # UserForm,
    # UserProfileForm,
    # AuthForm,
)


# My App


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated:
                #     cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(EcomMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["myname"] = "Dipak Niroula"
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 8)
        page_number = self.request.GET.get("page")
        print(page_number)
        product_list = paginator.get_page(page_number)
        context["product_list"] = product_list
        return context


class AllProductsView(EcomMixin, TemplateView):
    template_name = "allproducts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allcategories"] = Category.objects.all()
        return context


class ProductDetailView(EcomMixin, TemplateView):
    template_name = "productdetail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs["slug"]
        product = Product.objects.get(slug=url_slug)
        product.view_count += 1
        product.save()
        context["product"] = product
        return context


class AddToCartView(EcomMixin, TemplateView):
    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs["pro_id"]
        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj,
                    product=product_obj,
                    rate=product_obj.selling_price,
                    quantity=1,
                    subtotal=product_obj.selling_price,
                )
                cart_obj.total += product_obj.selling_price
                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session["cart_id"] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj,
                product=product_obj,
                rate=product_obj.selling_price,
                quantity=1,
                subtotal=product_obj.selling_price,
            )
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        return context


class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = self.request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()

        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()

        elif action == "cargo":
            cargo_id = self.request.GET.get("id")
            cargo = Cargo.objects.filter(id=int(cargo_id)).first()
            cp_obj.cargo = cargo

            # Recalculate the subtotal
            cp_obj.subtotal = (cp_obj.rate*cp_obj.quantity)+cp_obj.cargo.price
            cp_obj.save()

            # Recalculate the total by summing all the subtotals
            total = CartProduct.objects \
                .filter(cart_id=cp_obj.cart_id) \
                .aggregate(Sum('subtotal'))
            cart_obj.total = total['subtotal__sum']
            cart_obj.save()

        return redirect("ecomapp:mycart")


class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("ecomapp:mycart")


class MyCartView(EcomMixin, TemplateView):
    template_name = "mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        cargo = Cargo.objects.all()
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context["cart"] = cart
        context["cargo_list"] = cargo
        return context


class CheckoutView(EcomMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("ecomapp:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context["cart"] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session["cart_id"]
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "Khalti":
                return redirect(
                    reverse("ecomapp:khaltirequest") + "?o_id=" + str(order.id)
                )
            elif pm == "Esewa":
                return redirect(
                    reverse("ecomapp:esewarequest") + "?o_id=" + str(order.id)
                )
        else:
            return redirect("ecomapp:home")
        return super().form_valid(form)


class KhaltiRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {"order": order}
        return render(request, "khaltirequest.html", context)


class KhaltiVerifyView(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        o_id = request.GET.get("order_id")
        print(token, amount, o_id)

        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {"token": token, "amount": amount}
        headers = {
            "Authorization": "Key test_secret_key_f59e8b7d18b4499ca40f68195a846e9b"
        }

        order_obj = Order.objects.get(id=o_id)

        response = requests.post(url, payload, headers=headers)
        resp_dict = response.json()
        if resp_dict.get("idx"):
            success = True
            order_obj.payment_completed = True
            order_obj.save()
        else:
            success = False
        data = {"success": success}
        return JsonResponse(data)


class EsewaRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {"order": order}
        return render(request, "esewarequest.html", context)


class EsewaVerifyView(View):
    def get(self, request, *args, **kwargs):
        import xml.etree.ElementTree as ET

        oid = request.GET.get("oid")
        amt = request.GET.get("amt")
        refId = request.GET.get("refId")

        url = "https://uat.esewa.com.np/epay/transrec"
        d = {
            "amt": amt,
            "scd": "epay_payment",
            "rid": refId,
            "pid": oid,
        }
        resp = requests.post(url, d)
        root = ET.fromstring(resp.content)
        status = root[0].text.strip()

        order_id = oid.split("_")[1]
        order_obj = Order.objects.get(id=order_id)

        if status != "Success":
            return redirect(f"/esewa-request/?o_id={order_id}")

        order_obj.payment_completed = True
        order_obj.save()
        return redirect("/")


class ProductOwnerRegistrationView(CreateView):
    template_name = "customerregistration.html"
    form_class = productOwnerRegistrationForm
    success_url = reverse_lazy("ecomapp:home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)

        send_mail("Welcome to STOPPS business", "Thank for registering on stopps", settings.EMAIL_HOST_USER,
        [email], fail_silently=False)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            return self.request.GET.get("next")
        else:
            return self.success_url


class CustomerRegistrationView(CreateView):
    template_name = "customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("ecomapp:home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)

        send_mail("Welcome to STOPPS business", "Thank for registering on stopps", settings.EMAIL_HOST_USER,
        [email], fail_silently=False)
        
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            return self.request.GET.get("next")
        else:
            return self.success_url


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("ecomapp:home")


class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:home")

    # form_valid method is a type of post method and is available in createview formview and updateview
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(
                self.request,
                self.template_name,
                {"form": self.form_class, "error": "Invalid credentials"},
            )

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            return self.request.GET.get("next")
        else:
            return self.success_url


class AboutView(EcomMixin, TemplateView):
    template_name = "about.html"


class ContactView(EcomMixin, TemplateView):
    template_name = "contactus.html"


class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['Customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context


class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and Customer.objects.filter(user=request.user).exists()
        ):
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("ecomapp:customerprofile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(
            Q(title__icontains=kw)
            | Q(description__icontains=kw)
            | Q(return_policy__icontains=kw)
        )
        print(results)
        context["results"] = results
        return context


class PasswordForgotView(FormView):
    template_name = "forgotpassword.html"
    form_class = PasswordForgotForm
    success_url = "/forgot-password/?m=s"

    def form_valid(self, form):
        # get email from user
        email = form.cleaned_data.get("email")
        # get current host ip/domain
        url = self.request.META["HTTP_HOST"]
        # get customer and then user
        customer = Customer.objects.get(user__email=email)
        # send mail to the user with email
        text_content = "Please Click the link below to reset your password. "
        user = customer.user
        html_content = (
            f"{url}/password-reset/{email}/{password_reset_token.make_token(user)}/"
        )

        send_mail(
            "Password Reset Link | Django STOPPS",
            text_content + html_content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=True,
        )
        return super().form_valid(form)


class PasswordResetView(FormView):
    template_name = "passwordreset.html"
    form_class = PasswordResetForm
    success_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        token = self.kwargs.get("token")
        if user is None or not password_reset_token.check_token(user, token):
            return redirect(reverse("ecomapp:passworforgot") + "?m=e")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data["new_password"]
        email = self.kwargs.get("email")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return super().form_valid(form)


# admin pages


class AdminLoginView(FormView):
    template_name = "adminpages/adminlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(
                self.request,
                self.template_name,
                {"form": self.form_class, "error": "Invalid credentials"},
            )
        return super().form_valid(form)


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if (
            not request.user.is_authenticated
            or not Admin.objects.filter(user=request.user).exists()
        ):
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminhome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(
            order_status="Order Received"
        ).order_by("-id")
        return context


class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = "adminpages/adminorderdetail.html"
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context


class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"


class AdminOrderStatuChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(
            reverse_lazy("ecomapp:adminorderdetail", kwargs={"pk": order_id})
        )


class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminproductlist.html"
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "allproducts"


class AdminProductCreateView(AdminRequiredMixin, CreateView):
    template_name = "adminpages/adminproductcreate.html"
    form_class = ProductForm
    success_url = reverse_lazy("ecomapp:adminproductlist")

    def form_valid(self, form):
        p = form.save()
        images = self.request.FILES.getlist("more_images")
        for i in images:
            ProductImage.objects.create(product=p, image=i)
        return super().form_valid(form)


# Linfox Page


class LinfoxLoginView(FormView):
    template_name = "linfox/linfoxlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:linfoxhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(
                self.request,
                self.template_name,
                {"form": self.form_class, "error": "Invalid credentials"},
            )
        return super().form_valid(form)


class LinfoxRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if (
            not request.user.is_authenticated
            or not Admin.objects.filter(user=request.user).exists()
        ):
            return redirect("/linfox-login/")
        return super().dispatch(request, *args, **kwargs)


class LinfoxHomeView(LinfoxRequiredMixin, TemplateView):
    template_name = "linfox/linfoxhome.html"


class LinfoxCargoListView(LinfoxRequiredMixin, ListView):
    template_name = "linfox/linfoxcargolist.html"
    queryset = Cargo.objects.all().order_by("-id")
    context_object_name = "allcargo"


class LinfoxCargoCreateView(LinfoxRequiredMixin, CreateView):
    template_name = "linfox/linfoxproductcreate.html"
    form_class = CargoForm
    success_url = reverse_lazy("ecomapp:linfoxproductcreate")

    def form_valid(self, form):
        p = form.save()
        images = self.request.FILES.getlist("more_images")
        for i in images:
            LinfoxImage.objects.create(cargo=p, image=i)
        return super().form_valid(form)


class AdminCargoDetailView(LinfoxRequiredMixin, DetailView):
    template_name = "adminpages/adminCargodetail.html"
    model = Cargo
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context


class AdminCargoStatuChangeView(LinfoxRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Cargo.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(
            reverse_lazy("ecomapp:adminocargodetail", kwargs={"pk": order_id})
        )


# class RegistrationView(CreateView):
#     template_name = "productownerregistration.html"
#     form_class = productOwnerRegistrationForm
#     success_url = reverse_lazy("ecomapp:home")

#     def form_valid(self, form):
#         username = form.cleaned_data.get("username")
#         password = form.cleaned_data.get("password")
#         email = form.cleaned_data.get("email")
#         user = User.objects.create_user(username, email, password)
#         form.instance.user = user
#         login(self.request, user)
#         return super().form_valid(form)

#     def get_success_url(self):
#         if "next" in self.request.GET:
#             next_url = self.request.GET.get("next")
#             return next_url
#         else:
#             return self.success_url

# product owner Page


class productOwnerLoginView(FormView):
    template_name = "productOwner/ProductOwnerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("ecomapp:pohome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and ProductOwner.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(
                self.request,
                self.template_name,
                {"form": self.form_class, "error": "Invalid credentials"},
            )
        return super().form_valid(form)


class productOwnerRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if (
            not request.user.is_authenticated
            or not ProductOwner.objects.filter(user=request.user).exists()
        ):
            return redirect("/product-login/")
        return super().dispatch(request, *args, **kwargs)


class productOwnerHomeView(productOwnerRequiredMixin, TemplateView):
    template_name = "productOwner/productOwnerhome.html"


class productOwnerListView(productOwnerRequiredMixin, ListView):
    template_name = "productOwner/productOwnerlist.html"
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "allproducts"


class productOwner1ListView(productOwnerRequiredMixin, ListView):
    template_name = "productOwner/productOwnerlist.html"
    queryset = User.objects.all().order_by("-id")
    context_object_name = "alluser"


# def sample_view(request):
#     current_user = request.user


class productOwnerCreateView(productOwnerRequiredMixin, CreateView):
    template_name = "productOwner/productCreatePcreate.html"
    form_class = ProductForm
    success_url = reverse_lazy("ecomapp:poproductcreate")

    def form_valid(self, form):
        p = form.save()
        images = self.request.FILES.getlist("more_images")
        for i in images:
            ProductImage.objects.create(cargo=p, image=i)
        return super().form_valid(form)


# class indexemail( CreateView):

#     def index(requests):
#       if requests.method == 'POST':
#         full_name = requests.POST.get('full_name')
#         county = requests.POST.get('county')
#         email = requests.POST.get('email')
#         send_mail(full_name, county, settings.EMAIL_HOST_USER,
#                   [email], fail_silently=False)
#         return render(requests, 'email_sent.html', {'email': email})

#       return render(requests, 'customerregistration.html', {})
