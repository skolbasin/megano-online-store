from json import loads

from django.test import TestCase

from .models import SiteSettings


class SiteSettingsTest(TestCase):
    def setUp(self) -> None:
        self.generic_settings = SiteSettings.objects.create()

    def test_first_instance(self) -> None:
        self.assertEqual(self.generic_settings.id, 1)

    def test_load(self) -> None:
        self.assertEqual(SiteSettings.load().id, 1)

    def test_load_cfg(self) -> None:
        with open("core/config/config.json", "r") as cfg:
            data = loads(cfg.read())
            self.generic_settings.load_config()
            self.assertEqual(data["cache_time"], self.generic_settings.cache_time)
            self.assertEqual(data["cache_active"], self.generic_settings.active)
