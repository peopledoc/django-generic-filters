from django.utils.translation import gettext_lazy as _

from django_genericfilters import forms as gf


class UserListForm(gf.FilteredForm):
    is_active = gf.ChoiceField(
        label=_("Status"), choices=(("yes", _("Active")), ("no", _("Unactive")))
    )

    is_staff = gf.ChoiceField(label=_("Staff"))

    is_superuser = gf.ChoiceField(label=_("Superuser"))

    def get_order_by_choices(self):
        return [
            ("date_joined", _(u"date joined")),
            ("last_login", _(u"last login")),
            ("last_name", _(u"Name")),
        ]
