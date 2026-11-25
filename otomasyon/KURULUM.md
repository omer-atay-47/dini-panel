# Paylaşım: Meta Business Suite ile planlama

Videolar **Meta Business Suite**'te (business.facebook.com) önceden planlanır; zamanı gelince Meta kendisi yayınlar. Bilgisayarın açık olması gerekmez.

- Giriş: **"Instagram ile devam et"** (Facebook hesabı gerekmez).
- Her gün **20:00** video (Reels), **20:05** hikâyesi (Türkiye saati).
- Planlanan ilk hafta: 26 Kasım - 2 Aralık 2026.

## Yeni video ekleme

1. Videoyu `videos/<id>.mp4` olarak koy, `data.json` içine bilgilerini ekle.
2. `otomasyon/schedule.json` içine tarihini ekle.
3. `python otomasyon/hikaye.py` çalıştır: `videos/story/<id>.mp4` oluşur.
4. Business Suite > **Reel oluştur**: videoyu yükle, açıklamayı panelden kopyala, **Program** ile tarih ve 20:00.
5. Business Suite > **Hikaye oluştur**: hikâye dosyasını yükle, **Program** ile aynı gün 20:05.
6. İçerik > Planlanmış listesinde ikisini de gör.
7. `schedule.json` satırına `"meta": true` ekle ve GitHub'a yükle. Panelde "Planlandı" görünür.

## Takvimdeki durumlar

- **Planlandı / Bugün 20:00:** Meta'da planlı.
- **Saati geçti:** yayın saati geçmiş; yayınlandığını Instagram'dan kontrol et (panel göremez).
- **Planlanmadı:** `"meta": true` yok; paylaşılmayacak.

Tarih veya saati Meta'da değiştirirsen `schedule.json` dosyasını da güncelle.

## Hikâye

- Videonun ilk 8-14 saniyesi, "YENİ VİDEO" ve "Tamamı profilimizde" yazısıyla.
- Planlanan hikâyeye dokununca videoya gidilmez. Bunu istiyorsan Instagram uygulamasında videoyu elle "hikâyene ekle" ile paylaş.

## Yedek yöntem (kullanılmıyor)

`otomasyon/post.py` Instagram API ile paylaşır; bunun için Meta geliştirici uygulaması, `IG_USER_ID` / `IG_TOKEN` gizli anahtarları ve `SITE_URL` değişkeni gerekir. Günlük zamanlaması kapalıdır; GitHub Actions'ta yalnızca elle çalışır ve varsayılan olarak deneme modundadır. `"meta": true` olan videoları atlar. Anahtarı sohbete yazma.

## Dikkat

- Videolar herkese açık bir sitede durur (GitHub Pages'in ücretsiz sürümü böyle çalışır).
