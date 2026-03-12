from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from apps.core.mixins import AppPermissionMixin
from apps.core.utils import log_audit_action
from .forms import SupplierForm, PurchaseOrderForm, PurchaseOrderItemForm
from .models import Supplier, PurchaseOrder, PurchaseOrderItem


class SupplierListView(AppPermissionMixin, ListView):
    permission_required = "suppliers.view_supplier"
    model = Supplier
    template_name = "suppliers/supplier_list.html"
    context_object_name = "suppliers"


class SupplierCreateView(AppPermissionMixin, SuccessMessageMixin, CreateView):
    permission_required = "suppliers.add_supplier"
    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/supplier_form.html"
    success_url = reverse_lazy("suppliers:supplier_list")
    success_message = "El proveedor fue creado correctamente."


class SupplierUpdateView(AppPermissionMixin, SuccessMessageMixin, UpdateView):
    permission_required = "suppliers.change_supplier"
    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/supplier_form.html"
    success_url = reverse_lazy("suppliers:supplier_list")
    success_message = "El proveedor fue actualizado correctamente."


class SupplierDeleteView(AppPermissionMixin, DeleteView):
    permission_required = "suppliers.delete_supplier"
    model = Supplier
    template_name = "suppliers/supplier_confirm_delete.html"
    success_url = reverse_lazy("suppliers:supplier_list")


class PurchaseOrderListView(AppPermissionMixin, ListView):
    permission_required = "suppliers.view_purchaseorder"
    model = PurchaseOrder
    template_name = "suppliers/purchase_order_list.html"
    context_object_name = "purchase_orders"

    def get_queryset(self):
        queryset = PurchaseOrder.objects.select_related("supplier", "created_by").prefetch_related("items")

        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        supplier_id = self.request.GET.get("supplier")

        if q:
            queryset = queryset.filter(
                Q(number__icontains=q) | Q(supplier__name__icontains=q)
            )

        if status:
            queryset = queryset.filter(status=status)

        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.object_list

        context["suppliers"] = Supplier.objects.filter(is_active=True).order_by("name")
        context["selected_q"] = self.request.GET.get("q", "")
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_supplier"] = self.request.GET.get("supplier", "")
        context["status_choices"] = PurchaseOrder.STATUS_CHOICES

        context["total_orders"] = queryset.count()
        context["total_draft"] = queryset.filter(status=PurchaseOrder.DRAFT).count()
        context["total_sent"] = queryset.filter(status=PurchaseOrder.SENT).count()
        context["total_received"] = queryset.filter(status=PurchaseOrder.RECEIVED).count()
        context["total_cancelled"] = queryset.filter(status=PurchaseOrder.CANCELLED).count()

        return context

class PurchaseOrderCreateView(AppPermissionMixin, SuccessMessageMixin, CreateView):
    permission_required = "suppliers.add_purchaseorder"
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = "suppliers/purchase_order_form.html"
    success_message = "La orden de compra fue creada correctamente."

    def get_initial(self):
        initial = super().get_initial()
        supplier = self.request.GET.get("supplier")
        if supplier:
            initial["supplier"] = supplier
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_audit_action(
            user=self.request.user,
            module="purchasing",
            action="create",
            object_type="PurchaseOrder",
            object_id=self.object.pk,
            object_repr=self.object.number,
            description="Orden de compra creada.",
        )
        return response


class PurchaseOrderUpdateView(AppPermissionMixin, SuccessMessageMixin, UpdateView):
    permission_required = "suppliers.change_purchaseorder"
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = "suppliers/purchase_order_form.html"
    success_message = "La orden de compra fue actualizada correctamente."

    def dispatch(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status != PurchaseOrder.DRAFT:
            messages.error(request, "Solo se pueden editar órdenes en borrador.")
            return redirect(order.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        log_audit_action(
            user=self.request.user,
            module="purchasing",
            action="update",
            object_type="PurchaseOrder",
            object_id=self.object.pk,
            object_repr=self.object.number,
            description="Orden de compra actualizada.",
        )
        return response


class PurchaseOrderDetailView(AppPermissionMixin, DetailView):
    permission_required = "suppliers.view_purchaseorder"
    model = PurchaseOrder
    template_name = "suppliers/purchase_order_detail.html"
    context_object_name = "purchase_order"

    def get_queryset(self):
        return PurchaseOrder.objects.select_related("supplier", "created_by").prefetch_related("items__product")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_edit"] = self.object.status == PurchaseOrder.DRAFT
        context["can_receive"] = self.object.status in [PurchaseOrder.DRAFT, PurchaseOrder.SENT]
        return context


@login_required
def purchase_order_add_item(request, pk):
    if not request.user.has_perms(["suppliers.change_purchaseorder", "suppliers.add_purchaseorderitem"]):
        raise PermissionDenied

    purchase_order = get_object_or_404(PurchaseOrder.objects.select_related("supplier"), pk=pk)

    if purchase_order.status != PurchaseOrder.DRAFT:
        messages.error(request, "Solo puedes agregar ítems a órdenes en borrador.")
        return redirect(purchase_order.get_absolute_url())

    if request.method == "POST":
        form = PurchaseOrderItemForm(request.POST, purchase_order=purchase_order)
        if form.is_valid():
            item = form.save(commit=False)
            item.purchase_order = purchase_order
            item.save()
            log_audit_action(
                user=request.user,
                module="purchasing",
                action="update",
                object_type="PurchaseOrderItem",
                object_id=item.pk,
                object_repr=f"{purchase_order.number} - {item.product.name}",
                description="Ítem agregado a orden de compra.",
            )
            messages.success(request, "Ítem agregado correctamente a la orden.")
            return redirect(purchase_order.get_absolute_url())
    else:
        form = PurchaseOrderItemForm(purchase_order=purchase_order)

    return render(
        request,
        "suppliers/purchase_order_item_form.html",
        {
            "purchase_order": purchase_order,
            "form": form,
        },
    )


@login_required
def purchase_order_delete_item(request, order_pk, item_pk):
    if not request.user.has_perms(["suppliers.change_purchaseorder", "suppliers.delete_purchaseorderitem"]):
        raise PermissionDenied

    purchase_order = get_object_or_404(PurchaseOrder, pk=order_pk)
    item = get_object_or_404(PurchaseOrderItem, pk=item_pk, purchase_order=purchase_order)

    if purchase_order.status != PurchaseOrder.DRAFT:
        messages.error(request, "Solo puedes eliminar ítems de órdenes en borrador.")
        return redirect(purchase_order.get_absolute_url())

    if request.method == "POST":
        item_repr = f"{purchase_order.number} - {item.product.name}"
        item_id = item.pk
        item.delete()
        log_audit_action(
            user=request.user,
            module="purchasing",
            action="delete",
            object_type="PurchaseOrderItem",
            object_id=item_id,
            object_repr=item_repr,
            description="Ítem eliminado de orden de compra.",
        )
        messages.success(request, "Ítem eliminado correctamente.")
        return redirect(purchase_order.get_absolute_url())

    return redirect(purchase_order.get_absolute_url())


@login_required
def purchase_order_mark_sent(request, pk):
    if not request.user.has_perm("suppliers.send_purchaseorder"):
        raise PermissionDenied

    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == "POST":
        if purchase_order.status != PurchaseOrder.DRAFT:
            messages.error(request, "Solo las órdenes en borrador pueden marcarse como enviadas.")
        elif not purchase_order.items.exists():
            messages.error(request, "Agrega al menos un ítem antes de marcar la orden como enviada.")
        else:
            purchase_order.status = PurchaseOrder.SENT
            purchase_order.save(update_fields=["status", "updated_at"])
            log_audit_action(
                user=request.user,
                module="purchasing",
                action="send",
                object_type="PurchaseOrder",
                object_id=purchase_order.pk,
                object_repr=purchase_order.number,
                description="Orden marcada como enviada.",
            )
            messages.success(request, "La orden fue marcada como enviada.")

    return redirect(purchase_order.get_absolute_url())


@login_required
def purchase_order_receive(request, pk):
    if not request.user.has_perm("suppliers.receive_purchaseorder"):
        raise PermissionDenied

    purchase_order = get_object_or_404(PurchaseOrder.objects.prefetch_related("items__product"), pk=pk)

    if request.method == "POST":
        try:
            purchase_order.receive(request.user)
            log_audit_action(
                user=request.user,
                module="purchasing",
                action="receive",
                object_type="PurchaseOrder",
                object_id=purchase_order.pk,
                object_repr=purchase_order.number,
                description="Orden recibida y stock actualizado.",
            )
            messages.success(request, "La orden fue recibida y el stock se actualizó correctamente.")
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))

    return redirect(purchase_order.get_absolute_url())


@login_required
def purchase_order_cancel(request, pk):
    if not request.user.has_perm("suppliers.cancel_purchaseorder"):
        raise PermissionDenied

    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == "POST":
        if purchase_order.status == PurchaseOrder.RECEIVED:
            messages.error(request, "No puedes cancelar una orden ya recibida.")
        else:
            purchase_order.status = PurchaseOrder.CANCELLED
            purchase_order.save(update_fields=["status", "updated_at"])
            log_audit_action(
                user=request.user,
                module="purchasing",
                action="cancel",
                object_type="PurchaseOrder",
                object_id=purchase_order.pk,
                object_repr=purchase_order.number,
                description="Orden cancelada.",
            )
            messages.success(request, "La orden fue cancelada.")

    return redirect(purchase_order.get_absolute_url())
