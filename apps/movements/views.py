from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from apps.core.mixins import AppPermissionMixin
from apps.core.utils import log_audit_action
from .forms import StockMovementForm
from .models import StockMovement


class StockMovementListView(AppPermissionMixin, ListView):
    permission_required = "movements.view_stockmovement"
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


class StockMovementCreateView(AppPermissionMixin, SuccessMessageMixin, CreateView):
    permission_required = "movements.add_stockmovement"
    model = StockMovement
    form_class = StockMovementForm
    template_name = "movements/movement_form.html"
    success_message = "El movimiento fue registrado correctamente."

    def get_initial(self):
        initial = super().get_initial()
        product = self.request.GET.get("product")
        movement_type = self.request.GET.get("movement_type")

        if product:
            initial["product"] = product

        if movement_type in dict(StockMovement.MOVEMENT_TYPES):
            initial["movement_type"] = movement_type

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["return_to_product"] = bool(self.request.GET.get("product"))
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        log_audit_action(
            user=self.request.user,
            module="movements",
            action="create",
            object_type="StockMovement",
            object_id=self.object.pk,
            object_repr=str(self.object),
            description="Movimiento de stock registrado.",
            metadata={
                "product_id": self.object.product_id,
                "movement_type": self.object.movement_type,
                "quantity": self.object.quantity,
            },
        )
        return response

    def get_success_url(self):
        if self.request.POST.get("return_to_product") and self.object.product_id:
            return reverse_lazy("inventory:product_detail", kwargs={"pk": self.object.product_id})
        return reverse_lazy("movements:movement_list")
