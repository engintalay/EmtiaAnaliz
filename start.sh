#!/bin/bash
# Uygulamayı başlatır

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "❌ Sanal ortam bulunamadı. Önce ./install.sh çalıştırın."
  exit 1
fi

# Yerel IP'yi bul
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "🚀 EmtiaAnaliz başlatılıyor..."
echo "📱 Telefon/tarayıcı: http://${LOCAL_IP}:8000"
echo "💻 Yerel:           http://localhost:8000"
echo ""
echo "Durdurmak için: Ctrl+C"
echo "---"

.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
