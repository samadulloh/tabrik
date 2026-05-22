# 🕌 Bayram Tabriklash Boti

Ramazon va Qurbon Hayiti kunlari foydalanuvchilarni avtomatik tabriklovchi Telegram bot.

## ⚙️ Sozlash

### 1. Bot token olish
1. Telegramda **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: `HayitTabrikBot`)
4. Tokenni oling va `bot.py` dagi `BOT_TOKEN` ga joylashtiring

### 2. O'rnatish va ishga tushirish

```bash
# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Botni ishga tushirish
python bot.py
```

### 3. Docker bilan ishga tushirish

```bash
docker build -t hayit-bot .
docker run -d --name hayit-bot hayit-bot
```

## 📋 Buyruqlar

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni ishga tushirish, ro'yxatga olish |
| `/tabrik` | Bayram tabrigini ko'rish |
| `/keyingi` | Keyingi bayram sanasi |
| `/help` | Yordam |

## 🗓 Bayram sanalari

| Bayram | Sana |
|--------|------|
| Ramazon Hayiti 2025 | 30 Mart 2025 |
| Qurbon Hayiti 2025 | 6 Iyun 2025 |
| Ramazon Hayiti 2026 | 20 Mart 2026 |
| Qurbon Hayiti 2026 | 27 May 2026 |

## 🔔 Avtomatik tabrik qanday ishlaydi?

Bot har kuni soat **08:00** da tekshiradi — agar bugun bayram bo'lsa, barcha `/start` bosgan foydalanuvchilarga tabrik xabar yuboradi.
