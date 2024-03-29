from django import forms

from cms.models import Page
from cms.utils.urlutils import static_with_version

from .wizard_pool import entry_choices, wizard_pool


def step2_form_factory(mixin_cls, entry_form_class, attrs=None):
    """
    Combines a form mixin with a form class, sets attrs to the resulting class.
    This is used to provide a common behavior/logic for all wizard content
    forms.
    """
    if attrs is None:
        self.language_code = kwargs.pop('wizard_language')
        super().__init__(*args, **kwargs)

    @property
    def required_fields(self):
        return [f for f in self.visible_fields() if f.field.required]

    @property
    def optional_fields(self):
        return [f for f in self.visible_fields() if not f.field.required]


class WizardOptionWidgets(forms.RadioSelect):
    template_name = 'cms/wizards/wizardoptionwidget.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        wizard = wizard_pool.get_entry(value)
        attrs.update(wizard.widget_attributes)
        return super().create_option(name, value, label, selected, index, subindex, attrs)


class WizardStep1Form(BaseFormMixin, forms.Form):

    class Media:
        css = {
            'all': (
                static_with_version('cms/css/cms.wizard.css'),
            )
        }
        js = (
            static_with_version('cms/js/dist/bundle.admin.base.min.js'),
            'cms/js/modules/cms.wizards.js',
        )

    page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
        required=False,
        widget=forms.HiddenInput
    )
    language = forms.CharField(widget=forms.HiddenInput)
    entry = forms.ChoiceField(choices=[], widget=WizardOptionWidgets())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set the entries here to get an up-to-date list of entries.
        self.fields['entry'].choices = entry_choices(
            user=self.user,
            page=self.page,
        )

    def get_wizard_entries(self):
        for entry in self['entry']:
            wizard = wizard_pool.get_entry(entry.choice_value)
            yield (entry, wizard)


class WizardStep2BaseForm(BaseFormMixin):
    user = None
