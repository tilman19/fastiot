import sys
import unittest
from unittest.mock import Mock

from fastiot.cli.external_service_helper import get_services_list
from fastiot.cli.model import ProjectConfig
from fastiot_tests.cli import service_test


class TestServiceImports(unittest.TestCase):

    def tearDown(self):
        for mod in ["fastiot_test", "fastiot_test.cli", "fastiot_test.cli.services"]:
            try:
                sys.modules.pop(mod)
            except KeyError:
                pass

    def test_find_integrated_services(self):

        services = get_services_list()
        self.assertIn('mariadb', services.keys())

    def test_import_extension_without_service(self):
        """ Test listing services when importing extension without additional services"""
        sys.modules['fastiot_test_module'] = Mock()  # Empty module => Nothing to import

        project_config = ProjectConfig(project_namespace='fastiot_test',
                                       extensions=['fastiot_test_module'])
        services_integrated = get_services_list()
        services_after_import = get_services_list(project_config)
        self.assertEqual(len(services_integrated), len(services_after_import))

    def test_import_extension_with_service(self):
        """ Test importing services from actual module file """
        sys.modules['fastiot_test_module.extension'] = service_test

        project_config = ProjectConfig(project_namespace='fastiot_test', extensions=['fastiot_test_module'])
        services = get_services_list(project_config)

        self.assertIn('test_service', services.keys())
        self.assertIn('mariadb', services.keys())


if __name__ == '__main__':
    unittest.main()
