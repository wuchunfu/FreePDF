#!/bin/bash

# 图标转换脚本 - 将 .ico 转换为 .icns

set -e

echo "开始转换图标..."

# 检查源图标文件
ICO_FILE="ui/logo/logo.ico"
ICNS_FILE="ui/logo/logo.icns"

if [ ! -f "$ICO_FILE" ]; then
    echo "错误: 找不到源图标文件 $ICO_FILE"
    exit 1
fi

# 创建临时目录
TEMP_DIR=$(mktemp -d)
ICONSET_DIR="$TEMP_DIR/logo.iconset"
mkdir -p "$ICONSET_DIR"

echo "临时目录: $TEMP_DIR"

# 使用sips工具从ico提取并转换为不同尺寸的png
# macOS的iconset需要以下尺寸: 16, 32, 64, 128, 256, 512, 1024
sizes=(16 32 64 128 256 512)

# 先转换ico为png
PNG_FILE="$TEMP_DIR/logo.png"
sips -s format png "$ICO_FILE" --out "$PNG_FILE" > /dev/null 2>&1

if [ ! -f "$PNG_FILE" ]; then
    echo "错误: 无法转换ico为png"
    exit 1
fi

echo "已转换为PNG格式"

# 生成不同尺寸的图标
for size in "${sizes[@]}"; do
    sips -z $size $size "$PNG_FILE" --out "$ICONSET_DIR/icon_${size}x${size}.png" > /dev/null 2>&1
    echo "生成 ${size}x${size} 图标"

    # 生成@2x版本
    if [ $size -le 512 ]; then
        size2x=$((size * 2))
        sips -z $size2x $size2x "$PNG_FILE" --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" > /dev/null 2>&1
        echo "生成 ${size}x${size}@2x 图标"
    fi
done

# 使用iconutil生成icns
iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE"

if [ -f "$ICNS_FILE" ]; then
    echo "✅ 成功生成图标: $ICNS_FILE"
else
    echo "❌ 生成图标失败"
    exit 1
fi

# 清理临时文件
rm -rf "$TEMP_DIR"
echo "清理临时文件完成"
