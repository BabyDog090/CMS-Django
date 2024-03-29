from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserObjectPermissionManager(models.Manager):
    def assign_perm(self, perm, user, obj):
        """
        Assigns permission with given ``perm`` for an instance ``obj`` and
        ``user``.
        """
            raise Exception("Object %s needs to be persisted first" % obj)
        filters = {
            'permission__codename': perm,
            'permission__content_type': ContentType.objects.get_for_model(obj),
            'user': user,
        }
        filters['object_pk'] = obj.pk
        self.filter(**filters).delete()


class UserObjectPermission(models.Model):
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_pk = models.CharField(_('object ID'), max_length=255)
    content_object = GenericForeignKey(fk_field='object_pk')
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), on_delete=models.CASCADE)

    objects = UserObjectPermissionManager()

    def save(self, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(self.content_object)
        if content_type != self.permission.content_type:
            raise ValidationError("Cannot persist permission not designed for "
                                  "this class (permission's type is %r and object's type is %r)"
                                  % (self.permission.content_type, content_type))
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ['user', 'permission', 'object_pk']
