from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext as _

from .wizard_base import Wizard


class AlreadyRegisteredException(Exception):
    pass


def entry_choices(user, page):
    """
    Yields a list of wizard entries that the current user can use based on their
    permission to add instances of the underlying model objects.
    """
    for entry in wizard_pool.get_entries():
        if entry.user_has_add_permission(user, page=page):
            yield (entry.id, entry.title)


class WizardPool:
    _entries = {}
    _discovered = False

    def __init__(self):
        return self._discovered

    def is_registered(self, entry, **kwargs):
        """
        Returns True if the provided entry is registered.

        NOTE: This method triggers pool discovery unless a «passive» kwarg
        is set to True
        """
        passive = kwargs.get('passive', False)
        if not passive:
            self._discover()
        return entry.id in self._entries

    def register(self, entry):
        """
        Registers the provided «entry».

        Raises AlreadyRegisteredException if the entry is already registered.
        """
        assert isinstance(entry, Wizard), u"entry must be an instance of Wizard"
        if self.is_registered(entry, passive=True):
            model = entry.get_model()
            raise AlreadyRegisteredException(
                _(u"A wizard has already been registered for model: %s") %
                model.__name__)
        else:
            self._entries[entry.id] = entry

    def unregister(self, entry):
        """
        If «entry» is registered into the pool, remove it.

        Returns True if the entry was successfully registered, else False.

        NOTE: This method triggers pool discovery.
        """
        assert isinstance(entry, Wizard), u"entry must be an instance of Wizard"
        if self.is_registered(entry, passive=True):
            del self._entries[entry.id]
            return True
        return False

    def get_entry(self, entry):
        """
        Returns the wizard from the pool identified by «entry», which may be a
        Wizard instance or its "id" (which is the PK of its underlying
        content-type).

        NOTE: This method triggers pool discovery.
        """
        self._discover()
        if isinstance(entry, Wizard):
            entry = entry.id
        return self._entries[entry]

    def get_entries(self):
        """
        Returns all entries in weight-order.

        NOTE: This method triggers pool discovery.
        """
        self._discover()
        return [value for (key, value) in sorted(
            self._entries.items(), key=lambda e: e[1].weight)]


wizard_pool = WizardPool()
