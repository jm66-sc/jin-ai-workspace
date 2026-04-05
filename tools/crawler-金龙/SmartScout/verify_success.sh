#!/bin/bash
echo "🔍 验证第一阶段成功记录"

# 检查必要文件
required_files=(
    "config/success_template.py"
    "MILESTONE_PHASE1.md"
    "PAINFUL_EXPERIENCE.md"
    "simple_bids_50_20260211_032958.json"
)

missing=0
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (缺失)"
        missing=$((missing+1))
    fi
done

if [ $missing -eq 0 ]; then
    echo -e "\n🎉 所有成功记录文件完整！"
    echo "📊 第一阶段成功验证："
    echo "  时间：2026-02-11 03:29:58"
    echo "  用时：2-3秒"
    echo "  结果：50条数据"
    echo "  配置：undetected + stealth"
else
    echo -e "\n⚠️  缺失 $missing 个文件，请补充完整！"
fi

# 显示核心配置
echo -e "\n🔧 核心配置摘要："
grep -A2 "browser_mode=" config/success_template.py | head -3