from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Service, RoomType, CleaningOrder, OrderService, Review
from .forms import OrderForm, ReviewForm

def home(request):
    return render(request,"cleaning/home.html",{"services":Service.objects.filter(active=True)[:3]})
def catalog(request):
    qs=Service.objects.filter(active=True).prefetch_related("room_types")
    room=request.GET.get("room")
    if room: qs=qs.filter(room_types__id=room)
    q=request.GET.get("q","").strip()
    if q: qs=qs.filter(Q(name__icontains=q)|Q(description__icontains=q))
    page=Paginator(qs.distinct(),12).get_page(request.GET.get("page"))
    return render(request,"cleaning/catalog.html",{"page":page,"rooms":RoomType.objects.all(),"selected_room":room,"q":q})
def calculator(request):
    services=Service.objects.filter(active=True)
    rooms=RoomType.objects.all()
    return render(request,"cleaning/calculator.html",{"services":services,"rooms":rooms})
def price_api(request):
    try:
        area=max(1,min(int(request.GET.get("area", "50")),10000))
        room=RoomType.objects.get(pk=request.GET.get("room"))
        ids=[int(x) for x in request.GET.getlist("service")]
        chosen=Service.objects.filter(pk__in=ids,active=True)
        total=sum((s.price_per_m2 for s in chosen),Decimal("0"))*area*room.coefficient
        return JsonResponse({"total":str(total.quantize(Decimal("0.01"))),"currency":"₽"})
    except (ValueError,RoomType.DoesNotExist):
        return JsonResponse({"error":"Выберите тип помещения и корректную площадь."},status=400)
def order_create(request):
    if request.method=="POST":
        form=OrderForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated:
                messages.info(request,"Войдите или зарегистрируйтесь, чтобы оформить заказ.")
                request.session["pending_order"]=request.POST.dict()
                return redirect("login")
            with transaction.atomic():
                order=form.save(commit=False); order.customer=request.user
                room_factor=order.room_type.coefficient
                order.total=sum((s.price_per_m2 for s in form.cleaned_data["services"]),Decimal("0"))*order.area*room_factor
                order.save()
                for service in form.cleaned_data["services"]:
                    OrderService.objects.create(order=order,service=service,price=service.price_per_m2)
                form.save_m2m()
            messages.success(request,f"Заказ №{order.pk} успешно создан.")
            return redirect("order_detail",pk=order.pk)
    else: form=OrderForm()
    return render(request,"cleaning/order_form.html",{"form":form})
@login_required
def account(request):
    orders=CleaningOrder.objects.filter(customer=request.user)
    page=Paginator(orders,20).get_page(request.GET.get("page"))
    return render(request,"cleaning/account.html",{"page":page})
@login_required
def order_detail(request,pk):
    order=get_object_or_404(CleaningOrder.objects.prefetch_related("items__service"),pk=pk,customer=request.user)
    review_form=ReviewForm()
    if request.method=="POST":
        review_form=ReviewForm(request.POST)
        if review_form.is_valid() and order.status=="done":
            review=review_form.save(commit=False); review.order=order; review.save()
            messages.success(request,"Спасибо за отзыв!")
            return redirect("order_detail",pk=pk)
    return render(request,"cleaning/order_detail.html",{"order":order,"review_form":review_form})
def about(request): return render(request,"cleaning/about.html")
def search(request):
    q=request.GET.get("q","").strip()
    results=Service.objects.filter(active=True).filter(Q(name__icontains=q)|Q(description__icontains=q)) if q else Service.objects.none()
    return render(request,"cleaning/search.html",{"results":results,"q":q})
def register(request):
    form=UserCreationForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        user=form.save(); login(request,user); messages.success(request,"Аккаунт создан.")
        return redirect("account")
    return render(request,"cleaning/register.html",{"form":form})
