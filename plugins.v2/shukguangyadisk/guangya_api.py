"""MoviePilot 存储接口兼容层。

保留原 GuangYaApi 实现，并补齐新版 MoviePilot StorageBase.get_item_strict 接口。
"""

from pathlib import Path
from typing import Optional

from app import schemas

from .guangya_api_legacy import GuangYaApi as _GuangYaApi


class GuangYaApi(_GuangYaApi):
    """在原光鸭云盘实现上增加新版 MoviePilot 兼容接口。"""

    def get_item_strict(self, path: Path) -> Optional[schemas.FileItem]:
        """严格查询文件或目录；当前远端实现沿用 get_item 的查询语义。"""
        return self.get_item(path)
