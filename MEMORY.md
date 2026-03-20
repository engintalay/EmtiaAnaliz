# EmtiaAnaliz — Proje Hafızası

## Proje Amacı
Coin, hisse senedi, emtia (altın, petrol vb.) için anlık veri çeken,
teknik analiz yapan, al/sat tavsiyesi veren, grafikli rapor üreten,
LMStudio tabanlı Türkçe sohbet botu. Mobil uyumlu PWA.

---

## Teknoloji Kararları

| Bileşen | Teknoloji | Neden |
|---|---|---|
| Backend | Python + FastAPI | Hızlı API, async destek |
| Veri (hisse/emtia) | Yahoo Finance Query API (httpx, direkt HTTP) | yfinance kütüphanesi bloklanıyordu |
| Veri (kripto) | CoinGecko REST API | Ücretsiz, geniş kapsam |
| Teknik Analiz | ta (pandas-ta değil) | Python 3.14 uyumlu, numba bağımlılığı yok |
| Grafik | Plotly → iframe embed | innerHTML ile script çalışmıyor, iframe çözüm |
| LLM | LMStudio (local) OpenAI-compat API | httpx async client |
| LLM Streaming | SSE (Server-Sent Events) | Token token canlı akış |
| Frontend | HTML/CSS/JS (vanilla) | Sade, hızlı, mobil uyumlu |
| PWA | manifest.json + service worker | Telefona uygulama olarak kurulabilir |
| Loglama | Python logging, günlük dosya | logs/YYYY-MM-DD.log |

---

## Mimari Akış

```
Kullanıcı (mobil/web chat)
    ↓
FastAPI Backend
    ├── POST /analyze
    │     ├── extract_symbol()     → serbest metinden sembol çıkar
    │     ├── param_parser.py      → RSI/MACD/BB/EMA/gün parametrelerini parse et
    │     ├── data_fetcher.py      → CoinGecko / Yahoo Finance Query API / CSV
    │     ├── technical.py         → Teknik göstergeler (RSI, MACD, BB, EMA...)
    │     ├── chart.py             → Plotly HTML grafik
    │     └── JSONResponse         → grafik + göstergeler (hemen döner)
    │
    └── POST /analyze/stream
          └── llm.py               → LMStudio SSE stream → token token yanıt
```

---

## Dosya Yapısı

```
EmtiaAnaliz/
├── main.py              # FastAPI app, /analyze ve /analyze/stream
├── data_fetcher.py      # Yahoo Finance Query API + CoinGecko + CSV
├── technical.py         # Teknik analiz (parametrik: RSI, MACD, BB, EMA)
├── chart.py             # Plotly grafik (dinamik EMA periyotları)
├── llm.py               # LMStudio async httpx, streaming + non-streaming
├── history.py           # Analiz geçmişi (data/history.json)
├── param_parser.py      # Form + serbest metin parametre parse
├── logger.py            # Günlük log (logs/YYYY-MM-DD.log)
├── templates/
│   └── index.html       # Mobil uyumlu PWA chat arayüzü
├── static/
│   ├── style.css        # Mobile-first CSS
│   ├── manifest.json    # PWA manifest
│   ├── sw.js            # Service Worker
│   └── icons/           # PWA ikonları (192, 512px)
├── data/
│   └── history.json     # Analiz geçmişi (otomatik oluşur)
├── logs/                # Günlük log dosyaları (gitignore'da)
├── MEMORY.md            # Bu dosya
├── install.sh           # Kurulum scripti
├── start.sh             # Başlatma scripti
├── .gitignore
└── requirements.txt
```

---

## Özellikler

### Veri Kaynakları
- **Kripto**: CoinGecko API (ücretsiz) — BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX, DOT, MATIC, LTC, LINK, UNI, ATOM, TRX
- **Hisse/Emtia**: Yahoo Finance Query API (direkt HTTP, User-Agent ile)
- **Takma adlar**: ALTIN→GC=F, PETROL→CL=F, BRENT→BZ=F, GUMUS→SI=F, BIST100→XU100.IS, DOLAR→USDTRY=X vb.
- **Fallback**: Kullanıcı CSV yükleyebilir

### Teknik Analiz (Parametrik)
- RSI (varsayılan: 14)
- MACD (varsayılan: 12/26/9)
- Bollinger Bands (varsayılan: 20)
- EMA (varsayılan: 9, 21, 50)
- Destek/Direnç (son 30 günün min/max)
- Hacim analizi
- Trend tespiti (EMA sıralaması)

### Parametre Değiştirme
- **Ayarlar panelinden**: Form alanları (RSI, MACD, BB, EMA, gün sayısı)
- **Serbest metinden**: "RSI 21 olsun", "180 günlük analiz", "EMA 9 21 100 200"
- Parametreler localStorage'a kaydedilir

### LLM Entegrasyonu
- LMStudio OpenAI-compat API: `http://localhost:1234/v1`
- Model seçimi: Ayarlar panelinden `/v1/models` otomatik listelenir
- **Streaming**: Token token canlı akış (SSE)
- **Thinking (düşünme süreci)**: Varsayılan KAPALI, ayarlardan açılabilir
- Sistem prompt: Türkçe finans analisti rolü, YALNIZCA Türkçe yanıt
- Timeout: 600 saniye (10 dakika)

### Arayüz
- Mobile-first responsive tasarım
- Alt sabit input bar (iOS safe-area uyumlu)
- Sohbet baloncukları
- Grafikler iframe içinde (Plotly interaktif)
- ⚙️ Ayarlar: bottom-sheet (mobil) / modal (masaüstü)
- PWA: Android "Ana ekrana ekle" / iOS Safari paylaş → ekle

### Loglama
- Dosya: `logs/YYYY-MM-DD.log` (günlük)
- Her istek: IP, girdi, sembol, model, parametreler
- Her veri çekme: sembol, satır sayısı
- Her analiz: fiyat, RSI, trend
- Her LLM yanıtı: token sayısı
- Hatalar: stack trace ile

### Hafıza / Geçmiş
- Her analiz `data/history.json`'a kaydedilir
- `GET /history?symbol=BTC` ile sorgulanabilir

---

## LMStudio Ayarları
- Varsayılan URL: `http://localhost:1234`
- Model: Ayarlar panelinden seçilir (otomatik listelenir), localStorage'a kaydedilir
- Finans konusunda eğitilmiş model önerilir

---

## Kurulum
```bash
./install.sh   # Sanal ortam + paket kurulumu (bir kez)
./start.sh     # Uygulamayı başlat (her seferinde)
```

Telefon erişimi: `http://BILGISAYAR_IP:8000` (aynı ağda)

---

## Bilinen Sorunlar / Notlar
- Yahoo Finance direkt HTTP ile çalışıyor (yfinance kütüphanesi değil)
- Plotly grafikleri `innerHTML` ile eklenince script çalışmıyor → iframe çözümü kullanıldı
- CSS ID seçici (`#settingsPanel`) class seçiciden (`.hidden`) daha yüksek öncelik → `style.display` ile kontrol edildi
- Python 3.14 üzerinde çalışıyor (pandas-ta/numba uyumsuz, ta kütüphanesi kullanıldı)
- Paralel istek desteği: veri çekme `asyncio.to_thread`, LLM `httpx async`

---

## Değişiklik Geçmişi

| Tarih | Değişiklik |
|---|---|
| 2026-03-20 | Proje başlatıldı, MEMORY.md oluşturuldu, git init |
| 2026-03-20 | Tüm modüller yazıldı (data_fetcher, technical, chart, llm, history, main, frontend) |
| 2026-03-20 | install.sh ve start.sh eklendi |
| 2026-03-20 | pandas-ta → ta (Python 3.14 uyumu) |
| 2026-03-20 | Sembol çıkarma: serbest metinden sembol parse |
| 2026-03-20 | Günlük log sistemi (IP, istek, hata) |
| 2026-03-20 | LMStudio timeout 600s |
| 2026-03-20 | PWA desteği (manifest, service worker, ikonlar) |
| 2026-03-20 | Mobil ekran düzeltmeleri (font, buton boyutu, safe-area) |
| 2026-03-20 | Analiz parametreleri dinamik (form + serbest metin) |
| 2026-03-20 | Yahoo Finance Query API (yfinance yerine) — ALTIN/BRENT/hisse düzeltildi |
| 2026-03-20 | Paralel istek: asyncio.to_thread + httpx async |
| 2026-03-20 | Thinking toggle (varsayılan kapalı) |
| 2026-03-20 | Grafik iframe ile gösterildi (script sorunu çözüldü) |
| 2026-03-20 | LLM streaming (SSE, token token canlı akış) |
| 2026-03-20 | Ayarlar paneli CSS specificity sorunu düzeltildi |
