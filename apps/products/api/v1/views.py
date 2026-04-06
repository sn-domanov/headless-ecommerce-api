from django.db.models import Count, Prefetch, Q
from django_filters import CharFilter, FilterSet
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.core.permissions import IsStaffOrReadOnly
from apps.products.api.v1.serializers import (
    BrandDetailSerializer,
    BrandListSerializer,
    BrandWriteSerializer,
    CategoryDetailSerializer,
    CategoryListSerializer,
    CategoryWriteSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductUpdateSerializer,
    VariantCreateSerializer,
    VariantDetailSerializer,
    VariantImageCreateSerializer,
    VariantImageDetailSerializer,
    VariantImageListSerializer,
    VariantImageUpdateSerializer,
    VariantListSerializer,
    VariantUpdateSerializer,
)
from apps.products.models import (
    Brand,
    Category,
    Product,
    Variant,
    VariantImage,
)


class ProductFilter(FilterSet):
    brand = CharFilter(field_name="brand__slug", lookup_expr="exact")
    category = CharFilter(method="filter_category")

    class Meta:
        model = Product
        fields = ["brand", "category"]

    def filter_category(self, queryset, name, value):
        try:
            category = Category.objects.get(slug=value)
        except Category.DoesNotExist:
            return queryset.none()

        descendants = category.get_descendants(include_self=True)

        return queryset.filter(category__in=descendants)


class WriteReturnDetailSerializerMixin:
    detail_serializer_class = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        if self.detail_serializer_class is None:
            raise AssertionError("detail_serializer_class must be set")

        read_serializer = self.detail_serializer_class(  # pylint: disable=not-callable
            serializer.instance,
            context=self.get_serializer_context(),
        )

        headers = self.get_success_headers(read_serializer.data)
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance = serializer.instance

        if getattr(instance, "_prefetched_objects_cache", None):
            # Invalidate the prefetch cache on the instance
            instance._prefetched_objects_cache = {}  # pylint: disable=protected-access

        if self.detail_serializer_class is None:
            raise AssertionError("detail_serializer_class must be set")

        read_serializer = self.detail_serializer_class(  # pylint: disable=not-callable
            instance,
            context=self.get_serializer_context(),
        )

        return Response(read_serializer.data)


class BrandViewSet(WriteReturnDetailSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = Brand.objects.all()
    lookup_field = "slug"
    # Disable the default pagination set in config.settings.base
    pagination_class = None
    detail_serializer_class = BrandDetailSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BrandListSerializer
        elif self.action == "retrieve":
            return BrandDetailSerializer
        if self.action in ["create", "update", "partial_update"]:
            return BrandWriteSerializer
        return BrandDetailSerializer


class CategoryViewSet(WriteReturnDetailSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]

    # TODO this introduces N+1 to Category queryset. Fix for treebeard
    queryset = Category.objects.all()
    lookup_field = "slug"
    pagination_class = None
    detail_serializer_class = CategoryDetailSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        elif self.action == "retrieve":
            return CategoryDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CategoryWriteSerializer
        else:
            return CategoryDetailSerializer


class ProductViewSet(WriteReturnDetailSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    filterset_class = ProductFilter
    lookup_field = "slug"
    detail_serializer_class = ProductDetailSerializer

    @property
    def _is_staff(self) -> bool:
        return bool(self.request.user and self.request.user.is_staff)

    # N.B. Using method also avoids accidental queryset reuse if the class is subclassed later
    def get_queryset(self):
        qs = Product.objects.all().order_by("-created_at")
        variant_qs = Variant.objects.all().order_by("sku")
        variant_images_qs = VariantImage.objects.all().order_by("order", "id")
        variants_count = Count("variants")

        if not self._is_staff:
            qs = qs.active()
            variant_qs = variant_qs.active()
            variant_images_qs = variant_images_qs.active()
            variants_count = Count("variants", filter=Q(variants__is_active=True))

        qs = qs.select_related("brand", "category")
        qs = qs.prefetch_related(
            Prefetch(
                "variants",
                to_attr="visible_variants",
                queryset=variant_qs.prefetch_related(
                    Prefetch("images", queryset=variant_images_qs)
                ),
            )
        )
        qs = qs.annotate(variants_count=variants_count)

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        elif self.action == "retrieve":
            return ProductDetailSerializer
        elif self.action == "create":
            return ProductCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ProductUpdateSerializer
        else:
            return ProductDetailSerializer


class VariantViewSet(WriteReturnDetailSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    lookup_field = "uuid"
    detail_serializer_class = VariantDetailSerializer

    @property
    def _is_staff(self) -> bool:
        return bool(self.request.user and self.request.user.is_staff)

    # Reserve `list` action for internal use (inventory, bulk management, etc.)
    def get_permissions(self):
        if self.action == "list":
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        qs = Variant.objects.all().order_by("sku")
        variant_images_qs = VariantImage.objects.all().order_by("order", "id")

        if not self._is_staff:
            qs = qs.active()
            variant_images_qs = variant_images_qs.active()

        qs = qs.select_related("product")
        qs = qs.prefetch_related(Prefetch("images", queryset=variant_images_qs))

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return VariantListSerializer
        elif self.action == "retrieve":
            return VariantDetailSerializer
        elif self.action == "create":
            return VariantCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return VariantUpdateSerializer
        else:
            return VariantDetailSerializer


class VariantImageViewSet(WriteReturnDetailSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    lookup_field = "uuid"
    detail_serializer_class = VariantImageDetailSerializer

    @property
    def _is_staff(self) -> bool:
        return bool(self.request.user and self.request.user.is_staff)

    # Reserve `list` action for internal use
    def get_permissions(self):
        if self.action == "list":
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        qs = VariantImage.objects.all().order_by("order", "id")

        if not self._is_staff:
            qs = qs.active()

        qs = qs.select_related("variant")
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return VariantImageListSerializer
        elif self.action == "retrieve":
            return VariantImageDetailSerializer
        elif self.action in ["create"]:
            return VariantImageCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return VariantImageUpdateSerializer
        else:
            return VariantImageDetailSerializer
