# Otomatik paylaşım: kurulum

Her gün 20:00'de (Türkiye saati) sıradaki video, **farklı Instagram hesabına** otomatik Reels olarak paylaşılır; hemen ardından o videoyu tanıtan kısa bir **hikâye** de paylaşılır.
Sistem GitHub'da ücretsiz çalışır: videolar GitHub Pages'te durur, paylaşımı GitHub Actions yapar.

Takvim: `otomasyon/schedule.json` (7 gün, 26 Kasım - 2 Aralık 2026). Paylaşılanlar `otomasyon/posted.json` içine yazılır.

## Sende olması gerekenler (bunları sen yapmalısın)

1. **Instagram hesabı** profesyonele çevrilmeli (Ayarlar > Hesap türü). **İşletme** seç: hikâyenin otomatik paylaşımı İçerik üreticisi hesabında çalışmayabilir.
2. **Meta uygulaması:** developers.facebook.com > Uygulama oluştur > **Instagram API with Instagram Login** ekle. Hesabını uygulamaya test kullanıcısı/rol olarak ekle.
3. İzinler: `instagram_business_basic`, `instagram_business_content_publish`.
4. Uygulama panelinden **uzun süreli (60 gün) erişim anahtarı** üret ve **Instagram kullanıcı kimliğini** not al.
5. GitHub deposunda **Settings > Secrets and variables > Actions**:
   - Secret `IG_USER_ID`: Instagram kullanıcı kimliği
   - Secret `IG_TOKEN`: erişim anahtarı
   - Variable `SITE_URL`: `https://KULLANICI_ADIN.github.io/dini-panel`
6. **Settings > Pages**: Branch `main`, klasör `/ (root)`.

Anahtarı sohbete yazma; yalnızca GitHub Secrets içine kendin yapıştır.

## Deneme (hiçbir şey paylaşmadan)

Actions sekmesi > "Günlük paylaşım" > Run workflow > `dry_run` = 1.
Günlükte "Paylaşılacak: meryem ..." ve açıklama metni görünmeli.

## Hikâye

- Dosyalar `videos/story/<id>.mp4`: videonun ilk 8-14 saniyesi, "YENİ VİDEO" ve "Tamamı profilimizde" yazısıyla.
- Yeni video eklenince `python otomasyon/hikaye.py` çalıştırılıp çıkan dosya GitHub'a yüklenmeli.
- Instagram, otomatik paylaşımda hikâyeye **bağlantı çıkartması** eklemeye izin vermez. Dokununca videoya giden hikâye istiyorsan Instagram uygulamasında videoyu elle "hikâyene ekle" ile paylaş.
- Hikâye paylaşılamazsa video yine paylaşılmış sayılır; Actions günlüğünde uyarı görünür.

## Dikkat

- Erişim anahtarı yaklaşık **60 günde** biter; bitmeden yenilemen gerekir.
- Videolar herkese açık bir sitede durur (GitHub Pages'in ücretsiz sürümü böyle çalışır).
- Gün atlanırsa sistem gecikmiş videoyu ertesi gün paylaşır; aynı video iki kez gitmez.
- Instagram Reels sınırlarına uygun: dikey, 40-45 sn, mp4 (H.264/AAC).
