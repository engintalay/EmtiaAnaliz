# 📈 EmtiaAnaliz

Coin, hisse senedi ve emtia için anlık teknik analiz yapan, LMStudio destekli Türkçe sohbet botu.

---

## Özellikler

- **Geniş varlık desteği**: BTC, ETH ve tüm kripto paralar · AAPL, THYAO gibi hisseler · Altın, Brent petrol, gümüş · Döviz çiftleri
- **Teknik analiz**: RSI, MACD, Bollinger Bands, EMA, destek/direnç, hacim
- **İnteraktif grafik**: Mum grafiği + göstergeler, mobilde tam ekran
- **Canlı LLM yorumu**: Token token streaming, Türkçe AL/SAT/BEKLE tavsiyesi
- **Parametrik analiz**: RSI/MACD/BB/EMA periyotlarını ayarlardan veya sohbetten değiştir
- **PWA**: Telefona uygulama olarak kurulabilir
- **Çevrimdışı fallback**: CSV dosyası yükleyerek analiz yap

---

## Kurulum

### Gereksinimler
- Python 3.10+
- [LMStudio](https://lmstudio.ai) (yerel LLM sunucusu)

### Adımlar

```bash
# 1. Repoyu klonla
git clone <repo-url>
cd EmtiaAnaliz

# 2. Kur (bir kez)
./install.sh

# 3. LMStudio'yu başlat, bir model yükle, Local Server'ı aç

# 4. Uygulamayı başlat
./start.sh
```

Tarayıcıdan aç: `http://localhost:8000`

Telefon/tablet (aynı ağda): `http://BILGISAYAR_IP:8000`

---

## Kullanım

### Temel Kullanım
Sohbet kutusuna sembol veya doğal dil yaz:

| Girdi | Sonuç |
|---|---|
| `BTC` | Bitcoin analizi |
| `BTC analiz et` | Bitcoin analizi |
| `AAPL` | Apple hisse analizi |
| `THYAO` | Türk Hava Yolları analizi |
| `altın` | Altın (XAU/USD) analizi |
| `brent petrol` | Brent ham petrol analizi |
| `DOLAR` | USD/TRY analizi |

### Parametre Değiştirme (Sohbetten)
```
BTC analiz et, RSI 21 olsun
ETH, 180 günlük analiz yap
AAPL, EMA 9 21 100 200
altın, MACD 8 21 5
```

### Ayarlar Paneli (⚙️)
- **LMStudio URL**: Varsayılan `http://localhost:1234`
- **Model seçimi**: "Modelleri Yükle" ile otomatik listele
- **Düşünme süreci**: Thinking modunu aç/kapat
- **Analiz parametreleri**: RSI, MACD, BB, EMA periyotları, veri gün sayısı

### CSV Yükleme
İnternet yoksa 📎 butonuyla CSV yükle. Beklenen sütunlar: `date, open, high, low, close, volume`

### Telefona Kurulum (PWA)
- **Android**: Chrome menüsü → "Ana ekrana ekle"
- **iPhone**: Safari → Paylaş → "Ana Ekrana Ekle"

---

## Desteklenen Semboller

### Kripto
`BTC` `ETH` `BNB` `SOL` `XRP` `DOGE` `ADA` `AVAX` `DOT` `MATIC` `LTC` `LINK` `UNI` `ATOM` `TRX`

### Emtia Takma Adları
| Yazım | Varlık |
|---|---|
| `ALTIN` veya `GOLD` | Altın (XAU/USD) |
| `PETROL` veya `OIL` | Ham Petrol (WTI) |
| `BRENT` | Brent Ham Petrol |
| `GUMUS` veya `SILVER` | Gümüş |
| `DOLAR` | USD/TRY |
| `EURO` | EUR/TRY |
| `BIST100` | BIST 100 Endeksi |
| `SP500` | S&P 500 |
| `NASDAQ` | NASDAQ |

Diğer tüm Yahoo Finance sembolleri de desteklenir: `GC=F`, `BZ=F`, `^GSPC` vb.

---

## Teknik Göstergeler

| Gösterge | Varsayılan | Değiştirme |
|---|---|---|
| RSI | 14 periyot | `RSI 21 olsun` |
| MACD | 12/26/9 | `MACD 8 21 5` |
| Bollinger Bands | 20 periyot | `BB 14` |
| EMA | 9, 21, 50 | `EMA 9 21 50 200` |
| Veri aralığı | 90 gün | `180 günlük analiz` |

---

## Loglar

Günlük log dosyaları `logs/` klasöründe tutulur:
```
logs/2026-03-20.log
logs/2026-03-21.log
...
```

---

## Geliştirme

```bash
# Geliştirme modunda başlat (hot-reload)
./start.sh

# Analiz geçmişini görüntüle
curl http://localhost:8000/history
curl http://localhost:8000/history?symbol=BTC

# Mevcut LMStudio modellerini listele
curl "http://localhost:8000/models?base_url=http://localhost:1234"
```

---

## Lisans

MIT
