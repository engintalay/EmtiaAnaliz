#!/bin/bash
# Kurulum scripti — ilk kez çalıştırın

set -e
cd "$(dirname "$0")"

echo "📦 Sanal ortam oluşturuluyor..."
python3 -m venv .venv

echo "⬆️  Pip güncelleniyor..."
.venv/bin/pip install --upgrade pip -q

echo "📥 Paketler yükleniyor..."
.venv/bin/pip install -r requirements.txt -q

echo ""
echo "✅ Kurulum tamamlandı!"
echo "👉 Başlatmak için: ./start.sh"
