from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import PermissionDenied
from .models import InfoNegocio, NegocioUser, Categoria, Subcategoria, Producto, TiendaTema
from colorfield.fields import ColorField
from colorfield.widgets import ColorWidget

class TiendaTemaInline(admin.StackedInline):
    model = TiendaTema
    can_delete = False
    max_num = 1
    min_num = 1
    verbose_name = 'Tema de la tienda'
    verbose_name_plural = 'Tema de la tienda'
    fields = ('color_primario', 'color_secundario')
    formfield_overrides = {
        ColorField: {'widget': ColorWidget},
    }

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(InfoNegocio)
class InfoNegocioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'mostrar_logo', 'mostrar_colores', 'slug', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
    readonly_fields = ['slug']
    inlines = [TiendaTemaInline]
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'descripcion', 'activo')
        }),
        ('Información de Contacto', {
            'fields': ('direccion', 'telefono', 'email', 'whatsapp', 'horario')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud'),
            'description': 'Ingrese las coordenadas usando punto (.) o coma (,) como separador decimal'
        }),
        ('Imágenes', {
            'fields': ('logo', 'img_portada', 'favicon')
        }),
    )

    def mostrar_colores(self, obj):
        try:
            return format_html(
                '<div style="display: flex; gap: 10px; align-items: center;">'
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ddd; border-radius: 4px;"></div>'
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ddd; border-radius: 4px;"></div>'
                '</div>',
                obj.tema.color_primario,
                obj.tema.color_secundario
            )
        except:
            return "Sin tema"
    mostrar_colores.short_description = 'Colores'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Asegurarse de que existe un tema para la tienda
        TiendaTema.objects.get_or_create(negocio=obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            negocio_user = NegocioUser.objects.filter(user=request.user).first()
            if negocio_user:
                return qs.filter(id=negocio_user.negocio.id)
            return qs.none()
        return qs

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        negocio_user = NegocioUser.objects.filter(user=request.user).first()
        return negocio_user and negocio_user.negocio == obj

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        if not obj or request.user.is_superuser:
            return True
        negocio_user = NegocioUser.objects.filter(user=request.user).first()
        return negocio_user and negocio_user.negocio == obj
    
    def mostrar_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.logo.url)
        return "Sin logo"
    mostrar_logo.short_description = 'Logo'

@admin.register(NegocioUser)
class NegocioUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'negocio']
    list_filter = ['negocio']
    search_fields = ['user__username', 'negocio__nombre']

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'negocio', 'mostrar_imagen']
    list_filter = ['negocio']
    search_fields = ['nombre']

    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.imagen.url)
        return "Sin imagen"
    mostrar_imagen.short_description = 'Imagen'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            negocio_user = NegocioUser.objects.filter(user=request.user).first()
            if negocio_user:
                return qs.filter(negocio=negocio_user.negocio)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "negocio" and not request.user.is_superuser:
            negocio_user = NegocioUser.objects.filter(user=request.user).first()
            if negocio_user:
                kwargs["queryset"] = InfoNegocio.objects.filter(id=negocio_user.negocio.id)
                kwargs["initial"] = negocio_user.negocio
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            negocio_user = NegocioUser.objects.filter(user=request.user).first()
            if negocio_user:
                obj.negocio = negocio_user.negocio
        super().save_model(request, obj, form, change)

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria']
    list_filter = ['categoria__negocio', 'categoria']
    search_fields = ['nombre', 'categoria__nombre']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            negocio_user = NegocioUser.objects.filter(user=request.user).first()
            if negocio_user:
                return qs.filter(categoria__negocio=negocio_user.negocio)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "categoria" and not request.user.is_superuser:
            negocio_user = NegocioUser.objects.filter(user=request.user).first()
            if negocio_user:
                kwargs["queryset"] = Categoria.objects.filter(negocio=negocio_user.negocio)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'mostrar_imagen', 'precio', 'stock', 'descuento', 'subcategoria', 'activo']
    list_filter = ['activo', 'subcategoria__categoria__negocio', 'subcategoria', 'created_at']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'stock', 'descuento', 'activo']

    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.imagen.url)
        return "Sin imagen"
    mostrar_imagen.short_description = 'Imagen'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            negocio_user = NegocioUser.objects.filter(user=request.user).first()
            if negocio_user:
                return qs.filter(subcategoria__categoria__negocio=negocio_user.negocio)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subcategoria" and not request.user.is_superuser:
            negocio_user = NegocioUser.objects.filter(user=request.user).first()
            if negocio_user:
                kwargs["queryset"] = Subcategoria.objects.filter(
                    categoria__negocio=negocio_user.negocio
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.site_header = "Administración de E-ComCuba"
admin.site.site_title = "E-ComCuba"
admin.site.index_title = "Panel de Administración"