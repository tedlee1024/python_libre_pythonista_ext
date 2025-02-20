from __future__ import annotations
from typing import Any, cast, Dict, List
from pathlib import Path
import json
import toml

from ..meta.singleton import Singleton
from ..config import Config
from .token import Token


class JsonConfig(metaclass=Singleton):
    """Singleton Class the Config Json."""

    def __init__(self) -> None:
        self._config = Config()
        self._cfg = toml.load(self._config.toml_path)
        self._requirements = cast(Dict[str, str], self._cfg["tool"]["oxt"]["requirements"])
        try:
            self._zip_preinstall_pure = cast(bool, self._cfg["tool"]["oxt"]["config"]["zip_preinstall_pure"])
        except Exception:
            self._zip_preinstall_pure = False
        try:
            self._auto_install_in_site_packages = cast(
                bool, self._cfg["tool"]["oxt"]["config"]["auto_install_in_site_packages"]
            )
        except Exception:
            self._auto_install_in_site_packages = False
        try:
            self._install_wheel = cast(bool, self._cfg["tool"]["oxt"]["config"]["install_wheel"])
        except Exception:
            self._install_wheel = False
        try:
            self._window_timeout = int(self._cfg["tool"]["oxt"]["config"]["window_timeout"])
        except Exception:
            self._window_timeout = 5
        try:
            self._dialog_desktop_owned = cast(bool, self._cfg["tool"]["oxt"]["config"]["dialog_desktop_owned"])
        except Exception:
            self._dialog_desktop_owned = False

        try:
            self._default_locale = cast(list, self._cfg["tool"]["oxt"]["config"]["default_locale"])
        except Exception:
            self._default_locale = ["en", "US"]
        # resource_dir_name
        try:
            self._resource_dir_name = cast(str, self._cfg["tool"]["oxt"]["config"]["resource_dir_name"])
        except Exception:
            self._resource_dir_name = "resources"
        try:
            self._resource_properties_prefix = cast(
                str, self._cfg["tool"]["oxt"]["config"]["resource_properties_prefix"]
            )
        except Exception:
            self._resource_properties_prefix = "pipstrings"

        try:
            self._isolate_windows = cast(List[str], self._cfg["tool"]["oxt"]["isolate"]["windows"])
        except Exception:
            self._isolate_windows = []

        try:
            self._sym_link_cpython = cast(bool, self._cfg["tool"]["oxt"]["config"]["sym_link_cpython"])
        except Exception:
            self._sym_link_cpython = False
        try:
            self._uninstall_on_update = cast(bool, self._cfg["tool"]["oxt"]["config"]["uninstall_on_update"])
        except Exception:
            self._uninstall_on_update = True
        try:
            self._install_on_no_uninstall_permission = cast(
                bool, self._cfg["tool"]["oxt"]["config"]["install_on_no_uninstall_permission"]
            )
        except Exception:
            self._install_on_no_uninstall_permission = True

        try:
            self._unload_after_install = cast(bool, self._cfg["tool"]["oxt"]["config"]["unload_after_install"])
        except Exception:
            self._unload_after_install = True

        try:
            self._run_imports = cast(list, self._cfg["tool"]["oxt"]["config"]["run_imports"])
        except Exception:
            self._run_imports = []

        try:
            self._log_indent = cast(int, self._cfg["tool"]["oxt"]["config"]["log_indent"])
        except Exception:
            self._log_indent = False

        # region tool.libre_pythonista.config
        try:
            self._cell_custom_prop_prefix = cast(
                str, self._cfg["tool"]["libre_pythonista"]["config"]["cell_custom_prop_prefix"]
            )
        except Exception:
            self._cell_custom_prop_prefix = "libre_pythonista_"

        try:
            self._cell_custom_prop_codename = cast(
                str, self._cfg["tool"]["libre_pythonista"]["config"]["cell_custom_prop_codename"]
            )
        except Exception:
            self._cell_custom_prop_codename = "codename"

        try:
            self._py_script_sheet_ctl_click = cast(
                str, self._cfg["tool"]["libre_pythonista"]["config"]["py_script_sheet_ctl_click"]
            )
        except Exception:
            self._py_script_sheet_ctl_click = "control_handler.py"

        try:
            self._py_script_sheet_on_calculate = cast(
                str, self._cfg["tool"]["libre_pythonista"]["config"]["py_script_sheet_on_calculate"]
            )
        except Exception:
            self._py_script_sheet_on_calculate = "share_event.py"

        try:
            self._general_codename = cast(str, self._cfg["tool"]["libre_pythonista"]["config"]["general_code_name"])
        except Exception:
            self._general_codename = "libre_pythonista"

        try:
            self._lp_default_log_format = cast(
                str, self._cfg["tool"]["libre_pythonista"]["config"]["lp_default_log_format"]
            )
        except Exception:
            self._lp_default_log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        try:
            self._macro_lp_sheet_ctl_click = cast(
                str, self._cfg["tool"]["libre_pythonista"]["config"]["macro_lp_sheet_ctl_click"]
            )
        except Exception:
            self._macro_lp_sheet_ctl_click = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        try:
            self._macro_sheet_on_calculate = cast(
                str, self._cfg["tool"]["libre_pythonista"]["config"]["macro_sheet_on_calculate"]
            )
        except Exception:
            self._macro_sheet_on_calculate = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        try:
            self._extension_version = cast(str, self._cfg["tool"]["poetry"]["version"])
        except Exception:
            self._extension_version = ""

        try:
            self._extension_license = cast(str, self._cfg["tool"]["poetry"]["license"])
        except Exception:
            self._extension_license = ""

        try:
            self._author_names = self._get_author_names(self._cfg)
        except Exception:
            self._author_names = []
        # endregion tool.libre_pythonista.config
        self._validate()
        self._warnings()

    def _get_author_names(self, cfg: Dict[str, Any]) -> List[str]:
        """Get the author names."""
        authors = cast(List[str], cfg["tool"]["poetry"]["authors"])
        # Author elements are in the format of: ":Barry-Thomas-Paul: Moss <4193389+Amourspirit@users.noreply.github.com>"
        # get the names
        author_names = []
        for author in authors:
            author_names.append(author.split("<")[0].strip())
        return author_names

    def update_json_config(self, json_config_path: Path) -> None:
        """Read and updates the config.json file."""
        with open(json_config_path, "r") as f:
            json_config = json.load(f)
        token = Token()
        json_config["py_pkg_dir"] = token.get_token_value("py_pkg_dir")
        json_config["lo_identifier"] = token.get_token_value("lo_identifier")
        json_config["lo_implementation_name"] = token.get_token_value("lo_implementation_name")
        json_config["extension_display_name"] = token.get_token_value("display_name")
        json_config["oxt_name"] = token.get_token_value("oxt_name")

        json_config["zipped_preinstall_pure"] = self._zip_preinstall_pure
        json_config["auto_install_in_site_packages"] = self._auto_install_in_site_packages
        json_config["install_wheel"] = self._install_wheel
        json_config["window_timeout"] = self._window_timeout
        json_config["dialog_desktop_owned"] = self._dialog_desktop_owned
        json_config["default_locale"] = self._default_locale
        json_config["resource_dir_name"] = self._resource_dir_name
        json_config["resource_properties_prefix"] = self._resource_properties_prefix
        json_config["isolate_windows"] = self._isolate_windows
        json_config["sym_link_cpython"] = self._sym_link_cpython
        json_config["uninstall_on_update"] = self._uninstall_on_update
        json_config["install_on_no_uninstall_permission"] = self._install_on_no_uninstall_permission
        json_config["unload_after_install"] = self._unload_after_install
        json_config["run_imports"] = self._run_imports
        # json_config["log_pip_installs"] = self._log_pip_installs
        json_config["log_indent"] = self._log_indent
        # update the requirements
        json_config["requirements"] = self._requirements
        json_config["has_locals"] = self._config.has_locals

        # region tool.libre_pythonista.config
        json_config["cell_cp_prefix"] = self._cell_custom_prop_prefix
        json_config["cell_cp_codename"] = f"{self._cell_custom_prop_prefix}{self._cell_custom_prop_codename}"
        json_config["general_code_name"] = self._general_codename
        json_config["lp_default_log_format"] = self._lp_default_log_format
        json_config["extension_version"] = self._extension_version
        json_config["extension_license"] = self._extension_license
        json_config["author_names"] = self._author_names
        json_config["macro_lp_sheet_ctl_click"] = self._macro_lp_sheet_ctl_click
        json_config["macro_sheet_on_calculate"] = self._macro_sheet_on_calculate
        json_config["py_script_sheet_ctl_click"] = self._py_script_sheet_ctl_click
        json_config["py_script_sheet_on_calculate"] = self._py_script_sheet_on_calculate
        # endregion tool.libre_pythonista.config

        # save the file
        with open(json_config_path, "w", encoding="utf-8") as f:
            json.dump(json_config, f, indent=4)

    def _validate(self) -> None:
        """Validate"""
        assert isinstance(self._requirements, dict), "requirements must be a dict"
        assert isinstance(self._zip_preinstall_pure, bool), "zip_preinstall_pure must be a bool"
        assert isinstance(self._auto_install_in_site_packages, bool), "auto_install_in_site_packages must be a bool"
        assert isinstance(self._install_wheel, bool), "install_wheel must be a bool"
        assert isinstance(self._window_timeout, int), "window_timeout must be an int"
        assert isinstance(self._dialog_desktop_owned, bool), "dialog_desktop_owned must be a bool"
        assert isinstance(self._default_locale, list), "default_locale must be a list"
        assert len(self._default_locale) > 0, "default_locale must have at least 1 elements"
        assert len(self._default_locale) < 4, "default_locale must have no more then three elements"
        assert isinstance(self._resource_dir_name, str), "resource_dir_name must be a string"
        assert len(self._resource_dir_name) > 0, "resource_dir_name must not be an empty string"
        assert isinstance(self._resource_properties_prefix, str), "resource_properties_prefix must be a string"
        assert len(self._resource_properties_prefix) > 0, "resource_properties_prefix must not be an empty string"
        assert isinstance(self._sym_link_cpython, bool), "sym_link_cpython must be a bool"
        assert isinstance(self._uninstall_on_update, bool), "uninstall_on_update must be a bool"
        assert isinstance(self._unload_after_install, bool), "unload_after_install must be a bool"
        assert isinstance(self._log_indent, int), "log_indent must be a int"
        assert isinstance(
            self._install_on_no_uninstall_permission, bool
        ), "_install_on_no_uninstall_permission must be a bool"
        assert isinstance(self._run_imports, list), "run_imports must be a list"
        # region tool.libre_pythonista.config
        assert isinstance(self._cell_custom_prop_prefix, str), "cell_custom_prop_prefix must be a string"
        assert isinstance(self._cell_custom_prop_codename, str), "cell_custom_prop_codename must be a string"
        assert isinstance(self._general_codename, str), "general_codename must be a string"
        assert isinstance(self._general_codename, str), "general_codename must be a string"
        assert isinstance(self._lp_default_log_format, str), "extension_version must be a string"
        assert self._lp_default_log_format, "lp_default_log_format must not be an empty string"
        # validate the extension version is a valid python version
        assert self._extension_version.count(".") == 2, "extension_version must contain two periods"
        # endregion tool.libre_pythonista.config

    def _warnings(self) -> None:
        warnings = []
        token = Token()
        dist_dir = cast(str, self._cfg["tool"]["oxt"]["config"]["dist_dir"])
        log_level = str(token.get_token_value("log_level"))
        log_format = str(token.get_token_value("log_format"))

        if self._log_indent > 0:
            warnings.append(f"'tool.oxt.config.log_indent' is set to {self._log_indent}. Set to 0 for production.")
        if dist_dir == "tmp_dist":
            warnings.append("'tool.oxt.config.dist_dir' is set to the default value of 'tmp_dist'.")
        if log_level != "INFO":
            warnings.append(f"'tool.oxt.config.log_level' is set to '{log_level}'. Set to INFO for production.")
        if "indent_str" in log_format:
            warnings.append(
                "'tool.oxt.config.log_format' contains 'indent_str'. This is for debugging. Remove for production."
            )
        if warnings:
            print("JsonConfig Warnings:")
            for warning in warnings:
                print(f"  {warning}")
            print()
