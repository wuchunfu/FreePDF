# PyInstaller runtime hook for OpenCV (cv2)
# 修复cv2递归导入问题

import sys
import os

# 在导入cv2之前,修复sys.path以避免递归导入
if hasattr(sys, '_MEIPASS'):
    # cv2可能在Resources/cv2,这会导致递归导入
    # 我们需要移除这个路径
    paths_to_remove = []
    for path in sys.path:
        if path.endswith('/cv2') or '/Resources/cv2' in path:
            paths_to_remove.append(path)

    for path in paths_to_remove:
        sys.path.remove(path)
        print(f"CV2 Hook: 移除路径 {path}")

