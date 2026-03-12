from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from .forms import StockMovementForm
from .models import StockMovement


class StockMovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = "movements/movement_list.html"
    context_object_name = "movements"
    paginate_by = 20

    def get_queryset(self):
        queryset = StockMovement.objects.select_related("product", "user").order_by("-created_at")

        search = self.request.GET.get("q")
        movement_type = self.request.GET.get("movement_type")

        if search:
            queryset = queryset.filter(
                Q(product__name__icontains=search)
                | Q(product__code__icontains=search)
                | Q(reason__icontains=search)
                | Q(reference__icontains=search)
            )

        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_q"] = self.request.GET.get("q", "")
        context["selected_type"] = self.request.GET.get("movement_type", "")
        context["movement_types"] = StockMovement.MOVEMENT_TYPES
        return context


class StockMovementCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = "movements/movement_form.html"
    success_url = reverse_lazy("movements:movement_list")
    success_message = "El movimiento fue registrado correctamente."

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
