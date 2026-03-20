# EmtiaAnaliz — Proje Hafızası

## Proje Amacı
Coin, hisse senedi, emtia (altın, petrol vb.) için anlık veri çeken,
teknik analiz yapan, al/sat tavsiyesi veren, grafikli rapor üreten,
LMStudio tabanlı Türkçe sohbet botu.

---

## Teknoloji Kararları

| Bileşen | Teknoloji | Neden |
|---|---|---|
| Backend | Python + FastAPI | Hızlı API, async destek |
| Veri (hisse/emtia) | yfinance | Ücretsiz, geniş kapsam |
| Veri (kripto) | ccxt + CoinGecko | Anlık kripto fiyatları |
| Teknik Analiz | pandas-ta | RSI, MACD, BB, EMA, SMA vb. |
| Grafik | Plotly | İnteraktif, HTML embed, mobil uyumlu |
| LLM | LMStudio (local) | OpenAI-compat API, finans modeli |
| Frontend | HTML/CSS/JS (vanilla) | Sade, hızlı, mobil uyumlu |
| Hafıza | MEMORY.md + analiz JSON | Proje + kullanıcı geçmişi |

---

## Mimari Akış

```
Kullanıcı (mobil/web chat)
    ↓
FastAPI Backend
    ├── data_fetcher.py  → yfinance / ccxt / CoinGecko / CSV fallback
    ├── technical.py     → Teknik göstergeler (RSI, MACD, BB, EMA, SMA...)
    ├── chart.py         → Plotly interaktif grafik
    └── llm.py           → LMStudio API → Türkçe yorum + al/sat tavsiyesi
    ↓
Chat arayüzü: Grafik + Tablo + LLM Yorumu
```

---

## Dosya Yapısı

```
EmtiaAnaliz/
├── main.py              # FastAPI app, route'lar
├── data_fetcher.py      # Veri çekme (yfinance, ccxt, CSV)
├── technical.py         # Teknik analiz hesaplamaları
├── chart.py             # Plotly grafik üretimi
├── llm.py               # LMStudio bağlantısı ve prompt yönetimi
├── history.py           # Analiz geçmişi kayıt/okuma
├── templates/
│   └── index.html       # Mobil uyumlu chat arayüzü
├── static/
│   └── style.css        # Mobile-first CSS
├── data/
│   └── history.json     # Analiz geçmişi (otomatik oluşur)
├── MEMORY.md            # Bu dosya — proje hafızası
├── .gitignore
└── requirements.txt
```

---

## Özellikler

### Veri
- Kripto: CoinGecko API (ücretsiz) + ccxt
- Hisse/Emtia: yfinance (Yahoo Finance)
- Fallback: Kullanıcı CSV yükleyebilir (internet yoksa)
- Desteklenen: BTC, ETH, her kripto / AAPL, THYAO gibi hisseler / XAUUSD (altın), BRENTOIL (petrol) vb.

### Teknik Analiz
- RSI (14)
- MACD (12, 26, 9)
- Bollinger Bands (20)
- EMA (9, 21, 50, 200)
- SMA (20, 50, 200)
- Hacim analizi
- Destek/Direnç seviyeleri

### LLM Entegrasyonu
- LMStudio OpenAI-compat API: `http://localhost:1234/v1`
- Model seçimi: Ayarlar panelinden, `/v1/models` otomatik listelenir
- LMStudio URL'si ayarlanabilir
- Seçilen model localStorage'a kaydedilir
- Sistem prompt: Türkçe finans analisti rolü

### Arayüz
- Mobile-first responsive tasarım
- Alt sabit input bar (mobil klavye uyumlu)
- Sohbet baloncukları
- Grafikler inline, kaydırılabilir
- ⚙️ Ayarlar paneli (model seçimi, LMStudio URL)
- Analiz geçmişi görüntüleme

### Hafıza / Geçmiş
- Her analiz `data/history.json` dosyasına kaydedilir
- Sohbet geçmişi oturum boyunca tutulur
- "Geçmişe bak" komutuyla önceki analizler sorgulanabilir

---

## LMStudio Ayarları
- Varsayılan URL: `http://localhost:1234`
- Model: Ayarlar panelinden seçilir (otomatik listelenir)
- Finans konusunda eğitilmiş model önerilir

---

## Kurulum (Yapılacak)
```bash
pip install fastapi uvicorn yfinance ccxt pandas pandas-ta plotly requests
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Değişiklik Geçmişi

| Tarih | Değişiklik |
|---|---|
| 2026-03-20 | Proje başlatıldı, MEMORY.md oluşturuldu, git init |
