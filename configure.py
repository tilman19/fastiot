from fastiot.cli.model import ModulePackageConfig

#extensions = ['fastiot.ext.print']

project_namespace = 'fastiot'
module_packages = [ModulePackageConfig(package_name='fastiot_sample_services',
                                       cache_name='fastiot:latest',
                                       extra_caches=['fastiot-dev:latest'])]
