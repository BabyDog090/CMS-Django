from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured

from cms import api
from cms.exceptions import ToolbarAlreadyRegistered, ToolbarNotRegistered
from cms.test_utils.testcases import CMSTestCase
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import ToolbarPool, toolbar_pool


class TestToolbar(CMSToolbar):
    pass



    def test_register_order(self):
        pool = ToolbarPool()
        pool.register(TestToolbar)
        pool.register(CMSToolbar)

        test_toolbar = OrderedDict()
        test_toolbar['cms.tests.test_toolbar_pool.TestToolbar'] = TestToolbar
        test_toolbar['cms.toolbar_base.CMSToolbar'] = CMSToolbar
        self.assertEqual(list(test_toolbar.keys()), list(pool.toolbars.keys()))

    def test_unregister(self):
        pool = ToolbarPool()
        pool.register(TestToolbar)
        pool.unregister(TestToolbar)
        self.assertEqual(pool.toolbars, {})

        self.assertRaises(ToolbarNotRegistered,
                          pool.unregister, TestToolbar)

    def test_settings(self):
        pool = ToolbarPool()
        toolbars = toolbar_pool.toolbars
        toolbar_pool.clear()
        with self.settings(CMS_TOOLBARS=['cms.cms_toolbars.BasicToolbar', 'cms.cms_toolbars.PlaceholderToolbar']):
            toolbar_pool.register(TestToolbar)
            self.assertEqual(len(list(pool.get_toolbars().keys())), 2)
            page = api.create_page("home", "simple.html", "en", published=True)
            page_edit_url_on = self.get_edit_on_url(page.get_absolute_url())

            with self.login_user_context(self.get_superuser()):
                response = self.client.get(page_edit_url_on)
                self.assertEqual(response.status_code, 200)
        toolbar_pool.toolbars = toolbars

    def test_watch_models(self):
        toolbar_pool.discover_toolbars()
        self.assertEqual(type(toolbar_pool.get_watch_models()), list)
