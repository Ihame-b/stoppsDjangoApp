from django.urls import path
from .views import (
    HomeView,
    AboutView,
    ContactView,
    AllProductsView,
    ProductDetailView,
    AddToCartView,
    MyCartView,
    ManageCartView,
    EmptyCartView,
    CheckoutView,
    KhaltiRequestView,
    KhaltiVerifyView,
    EsewaRequestView,
    EsewaVerifyView,
    CustomerRegistrationView,
    CustomerLogoutView,
    CustomerLoginView,
    CustomerProfileView,
    CustomerOrderDetailView,
    SearchView,
    PasswordForgotView,
    PasswordResetView,
    AdminLoginView,
    AdminHomeView,
    AdminOrderDetailView,
    AdminOrderListView,
    AdminOrderStatuChangeView,
    AdminProductListView,
    AdminProductCreateView,
    LinfoxCargoCreateView,
    LinfoxHomeView,
    LinfoxCargoListView,
    ProductOwnerRegistrationView,
    productOwnerCreateView,
    productOwnerHomeView,
    productOwnerListView,
    productOwnerLoginView,
)


app_name = "ecomapp"
urlpatterns = [
    # Client side pages
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact-us/", ContactView.as_view(), name="contact"),
    path("all-products/", AllProductsView.as_view(), name="allproducts"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="productdetail"),
    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    path("manage-cart/<int:cp_id>/", ManageCartView.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("khalti-request/", KhaltiRequestView.as_view(), name="khaltirequest"),
    path("khalti-verify/", KhaltiVerifyView.as_view(), name="khaltiverify"),
    path("esewa-request/", EsewaRequestView.as_view(), name="esewarequest"),
    path("esewa-verify/", EsewaVerifyView.as_view(), name="esewaverify"),
    path("register/", CustomerRegistrationView.as_view(), name="customerregistration"),
    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),
    path("profile/", CustomerProfileView.as_view(), name="customerprofile"),
    path(
        "profile/order-<int:pk>/",
        CustomerOrderDetailView.as_view(),
        name="customerorderdetail",
    ),
    path("search/", SearchView.as_view(), name="search"),
    path("forgot-password/", PasswordForgotView.as_view(), name="passworforgot"),
    path(
        "password-reset/<email>/<token>/",
        PasswordResetView.as_view(),
        name="passwordreset",
    ),
    # Admin Side pages
    path("admin-login/", AdminLoginView.as_view(), name="adminlogin"),
    path("admin-home/", AdminHomeView.as_view(), name="adminhome"),
    path(
        "admin-order/<int:pk>/", AdminOrderDetailView.as_view(), name="adminorderdetail"
    ),
    path("admin-all-orders/", AdminOrderListView.as_view(), name="adminorderlist"),
    path(
        "admin-order-<int:pk>-change/",
        AdminOrderStatuChangeView.as_view(),
        name="adminorderstatuschange",
    ),
    path(
        "admin-product/list/", AdminProductListView.as_view(), name="adminproductlist"
    ),
    path(
        "admin-product/add/",
        AdminProductCreateView.as_view(),
        name="adminproductcreate",
    ),
    # Linfox
    #     path("linfox-login/", LinfoxLoginView.as_view(), name="linfoxlogin"),
    path("linfox-home/", LinfoxHomeView.as_view(), name="linfoxhome"),
    path("linfox-cargo/list/", LinfoxCargoListView.as_view(), name="linfoxcargolist"),
    path(
        "linfox-cargo/add/", LinfoxCargoCreateView.as_view(), name="linfoxproductcreate"
    ),
    #     path("admin-cargo/<int:pk>/", AdminCargoDetailView.as_view(), name="adminocargodetail"),
    #     path("admin-cargo-<int:pk>-change/", AdminCargoStatuChangeView.as_view(), name="admincargostatuschange"),
    #
    # Product Owner
    path("product-login/", productOwnerLoginView.as_view(), name="productOwnerlogin"),
    path("po-home/", productOwnerHomeView.as_view(), name="pohome"),
    path("po-pro/list/", productOwnerListView.as_view(), name="poproductlist"),
    path("po-pro/add/", productOwnerCreateView.as_view(), name="poproductcreate"),
    path("poregister/", ProductOwnerRegistrationView.as_view(), name="poregistration"),
    #     path("email/", indexemail.as_view(), name="email"),
]
