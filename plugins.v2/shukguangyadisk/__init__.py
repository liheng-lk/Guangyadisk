"""Shuk-光鸭云盘插件入口。

主实现保留在 _plugin_legacy.py，本入口负责当前 fork 的版本与维护者元数据。
"""

from ._plugin_legacy import ShukGuangYaDisk

# fork 维护版本元数据
ShukGuangYaDisk.plugin_version = "2.2.4"
ShukGuangYaDisk.plugin_author = "liheng-lk"
ShukGuangYaDisk.author_url = "https://github.com/liheng-lk/Guangyadisk"

__all__ = ["ShukGuangYaDisk"]
