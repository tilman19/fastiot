from enum import Enum
from typing import Optional

import typer

from fastiot.cli.model import ProjectConfig
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS


class ToPrint(str, Enum):
    configs = 'configs'
    deploy_configs = 'deploy_configs'
    library_package = 'library_package'
    library_setup_py_dir = 'library_setup_py_dir'
    module_package_names = 'module_package_names'
    modules_to_build = 'modules_to_build'
    npm_test_dir = 'npm_test_dir'
    test_config = 'test_config'
    test_package = 'test_package'


_name_help = """
Name can be any of:\n
* configs ... prints all configs, therefore the test config if specified and all deploy configs.\n
* deploy_configs ... prints all deploy configs.\n
* library_package ... prints the specified library package.\n
* library_setup_py_dir ... prints the library directory which includes the setup.py. If unset, nothing will be 
printed.\n
* module_package_names ... prints all packages which include regular modules.\n
* modules_to_build ... prints all modules which can be built.\n
* npm_test_dir ... prints the npm dir for testing.\n
* test_config ... prints the name of the test config.\n
* test_package ... prints the package for testing.\n
"""


def check_name(name: str):
    included = True
    try:
        ToPrint(name)
    except ValueError:
        included = False

    if included is False:
        raise typer.BadParameter(f"Parameter for name is not valid: '{name}'")
    return name


@app.command('print', context_settings=DEFAULT_CONTEXT_SETTINGS)
def print_cmd(name: str = typer.Argument(..., help=_name_help, callback=check_name),
              config: Optional[str] = typer.Option(None,
                                                   help="Only applicable if <name> is modules_to_build. If specified, "
                                                        "it doesn't print modules which are not needed for the "
                                                        "configuration."),
              platform: Optional[str] = typer.Option(None,
                                                     help="Only applicable if <name> is modules_to_build. If "
                                                          "specified, it doesn't print modules which cannot be built "
                                                          "for the platform. Can be used together with --config "
                                                          "flag.")):
    project_config = get_default_context().project_config
    platforms = platform.split(',') if platform else []
    if name == 'configs':
        _print_test_config(project_config=project_config)
        _print_deploy_configs(project_config=project_config)
    elif name == 'deploy_configs':
        _print_deploy_configs(project_config=project_config)
    elif name == 'library_package':
        if project_config.library_package != '':
            print(project_config.library_package)
    elif name == 'library_setup_py_dir':
        if project_config.library_setup_py_dir != '':
            print(project_config.library_setup_py_dir)
    elif name == 'module_package_names':
        for package in project_config.module_packages:
            print(package.package_name)
    elif name == 'modules_to_build':
        if config is not None:
            # It doesn't make a difference which parameters are given here. You may refactor make_context's
            # get_config function to not use these variables always.
            config = project_config.get_config(
                config_name=config,
                docker_registry=None,
                tag=None,
                do_override_configs_with_env_variables=False
            )
            module_names_to_build = project_config.get_module_names_to_build_specified_by_config(config=config)
        else:
            module_names_to_build = project_config.all_module_names

        for module_name in module_names_to_build:
            if len(platforms) > 0:
                manifest = project_config.read_manifest(module_name=module_name)
                platforms_in_manifest = [p.value for p in manifest.platforms]
                if len([p for p in platforms if p in platforms_in_manifest]) == 0:
                    continue
            print(module_name)
    elif name == 'npm_test_dir':
        if project_config.npm_test_dir != '':
            print(project_config.npm_test_dir)
    elif name == 'test_config':
        _print_test_config(project_config=project_config)
    elif name == 'test_package':
        if project_config.test_package != '':
            print(project_config.test_package)


def _print_deploy_configs(project_config: ProjectConfig):
    for config in [*project_config.deploy_configs]:
        print(config)


def _print_test_config(project_config: ProjectConfig):
    if project_config.test_config != '':
        print(project_config.test_config)
