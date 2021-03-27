from common.serializer import BaseDynamicFieldModelSerializer
from inventory.models import Group, Permission
from rest_framework import serializers
from drf_spectacular.utils import extend_schema,extend_schema_view
from api.v1.fields.custom import create_foreign_key_field, create_foreign_field
from .permission import PermissionSerializer

class GroupBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ( 'name', 'uuid')


class GroupSerializer(BaseDynamicFieldModelSerializer):

    parent = GroupBaseSerializer(read_only=True, many=False)
    parent_id = create_foreign_key_field(serializers.IntegerField)(
        model_cls=Group, 
        field_name='id', 
        path='/api/v1/tenant/{parent_lookup_tenant}/group/', 
        method='get', 
        page_type='TreeList', 
        source='parent.id', 
        default=None,
    )

    parent_name = create_foreign_field(serializers.CharField)(
        model_cls=Group, 
        field_name='name', 
        path='/api/v1/tenant/{parent_lookup_tenant}/group/', 
        method='get', 
        page_type='TreeList', 
        label='上级组织', 
        read_only=True, 
        source='parent.name', 
        default=None,
    )

    children = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    set_permissions = create_foreign_key_field(serializers.ListField)(
        model_cls=Permission, 
        field_name='uuid', 
        path='/api/v1/tenant/{parent_lookup_tenant}/permission/', 
        method='get', 
        page_type='TreeList', 
        child=serializers.CharField(),
        write_only=True,
    )
    class Meta:
        model = Group

        fields = ( 
            'id', 'uuid', 'name', 'parent', 'parent_id', 'parent_name', 'permissions', 'children',
            'set_permissions',
        )

        extra_kwargs = {
            'parent_id': {'blank': True}
        }

    def get_permissions(self, instance):
        permissions = instance.permissions.all()
        ret = []
        for p in permissions:
            o = PermissionSerializer(p)
            ret.append(o.data)

        return ret        
    
    def create(self, validated_data):
        name = validated_data.get('name')
        parent_id = validated_data.get('parent').get('id')
        tenant = self.context['tenant']

        set_permissions = validated_data.pop('set_permissions', None)

        parent = Group.valid_objects.filter(id=parent_id).first()

        o: Group = Group.valid_objects.create(tenant=tenant, name=name, parent=parent)

        if set_permissions is not None:
            o.permissions.clear()
            for p_uuid in set_permissions:
                p = Permission.objects.filter(uuid=p_uuid).first()
                if p is not None:
                    o.permissions.add(p)

        return o

    def get_children(self, instance):
        qs = Group.valid_objects.filter(parent=instance).order_by('id')
        return [GroupBaseSerializer(q).data for q in qs]
    

# for openapi

class GroupListResponseSerializer(GroupSerializer):
    class Meta:
        model = Group
        fields = ( 'id', 'name', 'parent_name', 'uuid', 'children' )


class GroupCreateRequestSerializer(GroupSerializer):
    class Meta:
        model = Group
        fields = ( 'id', 'uuid', 'name', 'parent_id', 'permissions', 'children', 'set_permissions' )

class GroupCreateResponseSerializer(GroupSerializer):
    class Meta:
        model = Group
        fields = ( 'id', 'uuid', 'name', 'parent', 'parent_id', 'parent_name',)