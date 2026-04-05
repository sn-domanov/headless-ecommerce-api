from rest_framework import serializers

from apps.products.models import Category


class CategoryBaseReadSerializer(serializers.ModelSerializer):
    parent_slug = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "slug",
            "name",
            "parent_slug",
            "parent_name",
        ]

    def get_parent_slug(self, obj):
        parent = getattr(obj, "_parent_cache", None) or obj.get_parent()
        return parent.slug if parent else None

    def get_parent_name(self, obj):
        parent = getattr(obj, "_parent_cache", None) or obj.get_parent()
        return parent.name if parent else None


class CategoryListSerializer(CategoryBaseReadSerializer):
    pass


class CategoryDetailSerializer(CategoryBaseReadSerializer):
    pass


class CategoryWriteSerializer(serializers.ModelSerializer):
    parent = (
        serializers.PrimaryKeyRelatedField(  # pyright: ignore[reportAssignmentType]
            queryset=Category.objects.all(),
            required=False,
            allow_null=True,
            write_only=True,
        )
    )

    class Meta:
        model = Category
        fields = [
            "name",
            "parent",
        ]

    def validate(self, attrs):
        # Prevent moving existing nodes via API
        if self.instance and "parent" in attrs:
            raise serializers.ValidationError(
                {"parent": "Changing parent is not allowed"}
            )
        return super().validate(attrs)

    def create(self, validated_data):
        parent = validated_data.pop("parent", None)

        if parent is None:
            return Category.add_root(**validated_data)

        return parent.add_child(**validated_data)
