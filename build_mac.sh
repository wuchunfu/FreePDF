#!/bin/bash

# macOS应用构建和打包脚本

set -e

echo "======================================"
echo "   FreePDF macOS 构建打包脚本 v5.1.0"
echo "======================================"
echo ""

# 配置变量
APP_NAME="FreePDF"
VERSION="5.1.0"
SPEC_FILE="build_mac.spec"

# 代码签名配置 (可选)
# 如果需要签名和公证,请设置以下变量:
# SIGN_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
# APPLE_ID="your-apple-id@email.com"
# TEAM_ID="YOUR_TEAM_ID"
# APP_PASSWORD="app-specific-password"

SIGN_IDENTITY="${SIGN_IDENTITY:-}"
ENABLE_SIGNING=false
ENABLE_NOTARIZATION=false

if [ -n "$SIGN_IDENTITY" ]; then
    ENABLE_SIGNING=true
    echo "✓ 已配置代码签名"
    if [ -n "$APPLE_ID" ] && [ -n "$TEAM_ID" ] && [ -n "$APP_PASSWORD" ]; then
        ENABLE_NOTARIZATION=true
        echo "✓ 已配置公证服务"
    fi
else
    echo "⚠ 未配置代码签名,将跳过签名步骤"
    echo "  提示: 设置环境变量 SIGN_IDENTITY 以启用签名"
fi

echo ""

# 步骤1: 清理旧文件
echo "[1/6] 清理旧的构建文件..."
rm -rf build dist
mkdir -p dist
echo "✓ 清理完成"
echo ""

# 步骤2: 检查图标
echo "[2/6] 检查应用图标..."
if [ ! -f "ui/logo/logo.icns" ]; then
    echo "  图标文件不存在,正在转换..."
    ./create_icon.sh
else
    echo "✓ 图标文件已存在"
fi
echo ""

# 步骤3: 构建应用
echo "[3/6] 使用PyInstaller构建应用..."
echo "  这可能需要几分钟时间,请耐心等待..."
pyinstaller "$SPEC_FILE" --clean --noconfirm

if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ 构建失败: 找不到应用包"
    exit 1
fi
echo "✓ 应用构建完成"
echo ""

# 步骤4: 代码签名 (如果配置)
if [ "$ENABLE_SIGNING" = true ]; then
    echo "[4/6] 对应用进行代码签名..."

    # 签名所有框架和库
    echo "  签名动态库和框架..."
    find "dist/${APP_NAME}.app/Contents/MacOS" -type f \( -name "*.dylib" -o -name "*.so" \) -exec \
        codesign --force --sign "$SIGN_IDENTITY" \
        --options runtime \
        --entitlements entitlements.plist \
        --timestamp {} \;

    find "dist/${APP_NAME}.app/Contents/Frameworks" -type d -name "*.framework" -exec \
        codesign --force --sign "$SIGN_IDENTITY" \
        --options runtime \
        --entitlements entitlements.plist \
        --timestamp {} \; 2>/dev/null || true

    # 签名主应用
    echo "  签名主应用包..."
    codesign --force --deep --sign "$SIGN_IDENTITY" \
        --options runtime \
        --entitlements entitlements.plist \
        --timestamp \
        "dist/${APP_NAME}.app"

    # 验证签名
    echo "  验证签名..."
    codesign --verify --deep --strict --verbose=2 "dist/${APP_NAME}.app"
    spctl --assess --verbose=4 --type execute "dist/${APP_NAME}.app" || true

    echo "✓ 代码签名完成"
else
    echo "[4/6] 跳过代码签名"
fi
echo ""

# 步骤5: 创建DMG
echo "[5/6] 创建DMG安装包..."
./create_dmg.sh

if [ ! -f "dist/${APP_NAME}_v${VERSION}_macOS.dmg" ]; then
    echo "❌ DMG创建失败"
    exit 1
fi
echo "✓ DMG创建完成"
echo ""

# 步骤6: DMG签名和公证 (如果配置)
if [ "$ENABLE_SIGNING" = true ]; then
    echo "[6/6] 对DMG进行签名..."
    codesign --sign "$SIGN_IDENTITY" \
        --timestamp \
        "dist/${APP_NAME}_v${VERSION}_macOS.dmg"

    echo "✓ DMG签名完成"

    if [ "$ENABLE_NOTARIZATION" = true ]; then
        echo ""
        echo "开始公证流程..."
        echo "  上传DMG到Apple公证服务..."

        # 提交公证
        SUBMIT_OUTPUT=$(xcrun notarytool submit \
            "dist/${APP_NAME}_v${VERSION}_macOS.dmg" \
            --apple-id "$APPLE_ID" \
            --team-id "$TEAM_ID" \
            --password "$APP_PASSWORD" \
            --wait)

        echo "$SUBMIT_OUTPUT"

        # 检查公证结果
        if echo "$SUBMIT_OUTPUT" | grep -q "status: Accepted"; then
            echo "✓ 公证成功"

            # 装订公证票据
            echo "  装订公证票据..."
            xcrun stapler staple "dist/${APP_NAME}_v${VERSION}_macOS.dmg"
            echo "✓ 公证票据装订完成"
        else
            echo "❌ 公证失败"
            echo "  请检查Apple Developer账号配置和应用权限设置"
        fi
    fi
else
    echo "[6/6] 跳过DMG签名和公证"
fi
echo ""

# 完成
echo "======================================"
echo "           构建完成! 🎉"
echo "======================================"
echo ""
echo "输出文件:"
echo "  - 应用包: dist/${APP_NAME}.app"
echo "  - 安装包: dist/${APP_NAME}_v${VERSION}_macOS.dmg"
echo ""

# 显示文件大小
ls -lh "dist/${APP_NAME}_v${VERSION}_macOS.dmg"

echo ""
echo "使用说明:"
echo "  1. 无签名版本可直接分发给用户安装"
echo "  2. 用户首次打开可能需要在系统设置中允许运行"
if [ "$ENABLE_SIGNING" = false ]; then
    echo ""
    echo "代码签名配置 (可选):"
    echo "  如需对应用进行签名和公证,请设置以下环境变量:"
    echo "    export SIGN_IDENTITY='Developer ID Application: Your Name (TEAM_ID)'"
    echo "    export APPLE_ID='your-apple-id@email.com'"
    echo "    export TEAM_ID='YOUR_TEAM_ID'"
    echo "    export APP_PASSWORD='app-specific-password'"
    echo ""
    echo "  然后重新运行此脚本"
fi
echo ""
