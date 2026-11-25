"""Günlük Instagram Reels + hikâye paylaşımı (GitHub Actions ile çalışır, yalnızca standart kütüphane).

Mantık:
  - schedule.json içinden bugünün tarihine ait ve henüz paylaşılmamış videoyu bulur.
  - Video, GitHub Pages adresinden (herkese açık https bağlantısı) Instagram'a verilir.
  - Paylaşılanlar posted.json içine yazılır; aynı video iki kez paylaşılmaz.
  - Reels yayınlandıktan sonra videos/story/<id>.mp4 hikâye olarak paylaşılır
    (hikâye hata verirse Reels kaydı korunur, yalnızca uyarı yazılır).

Ortam değişkenleri:
  IG_USER_ID, IG_TOKEN  : Instagram hesabı (GitHub "Secrets" içinde saklanır)
  SITE_URL              : örn. https://KULLANICI.github.io/dini-panel
  DRY_RUN=1             : hiçbir şey paylaşmadan sadece ne yapacağını yazar
"""
import json, os, sys, time, datetime, urllib.parse, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://graph.instagram.com/v21.0"


def load(path, default):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def call(method, url, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Instagram hatası {e.code}: {e.read().decode()[:500]}")


def today_tr():
    # Türkiye saati (UTC+3)
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).date().isoformat()


def publish(uid, token, fields):
    """Kapsayıcı oluşturur, Instagram videoyu işleyene kadar bekler, yayınlar."""
    c = call("POST", f"{API}/{uid}/media", {**fields, "access_token": token})
    cid = c["id"]
    for _ in range(40):  # en çok ~10 dk bekle
        time.sleep(15)
        st = call("GET", f"{API}/{cid}?fields=status_code&access_token={urllib.parse.quote(token)}")
        print("durum:", st.get("status_code"))
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Video işlenemedi: {st}")
    else:
        raise SystemExit("Zaman aşımı: video işlenmedi.")
    return call("POST", f"{API}/{uid}/media_publish", {"creation_id": cid, "access_token": token})


def save(posted):
    with open(os.path.join(ROOT, "otomasyon/posted.json"), "w", encoding="utf-8") as f:
        json.dump(posted, f, ensure_ascii=False, indent=1)


def main():
    dry = os.environ.get("DRY_RUN") == "1"
    schedule = load("otomasyon/schedule.json", [])
    posted = load("otomasyon/posted.json", [])
    data = load("data.json", {"videolar": []})
    videos = {v["id"]: v for v in data["videolar"]}
    done = {p["id"] for p in posted}
    today = os.environ.get("FORCE_DATE") or today_tr()

    due = [s for s in schedule if s["id"] not in done and s["tarih"] <= today]
    if not due:
        print(f"{today}: paylaşılacak video yok.")
        return
    item = sorted(due, key=lambda s: s["tarih"])[0]  # gecikmiş varsa en eskisinden başla
    v = videos.get(item["id"])
    if not v:
        raise SystemExit(f"data.json içinde {item['id']} yok.")
    caption = item.get("aciklama") or (v["aciklama"] + "\n\n" + " ".join(v["etiketler"]))
    site = os.environ.get("SITE_URL", "").rstrip("/")
    video_url = f"{site}/{v['dosya']}"
    print(f"Paylaşılacak: {item['id']} ({item['tarih']}) -> {video_url}")
    story_file = f"videos/story/{item['id']}.mp4"
    story_url = f"{site}/{story_file}" if os.path.exists(os.path.join(ROOT, story_file)) else None
    print(f"Hikâye: {story_url or 'dosya yok, hikâye paylaşılmayacak'}")
    if dry:
        print("DRY_RUN: paylaşım yapılmadı.\nAçıklama:\n" + caption)
        return

    uid, token = os.environ["IG_USER_ID"], os.environ["IG_TOKEN"]
    pub = publish(uid, token, {"media_type": "REELS", "video_url": video_url, "caption": caption, "share_to_feed": "true"})
    record = {"id": item["id"], "tarih": today, "ig_media_id": pub.get("id")}
    posted.append(record)
    save(posted)  # hikâyeden önce yazılır: aynı Reels ikinci kez gitmesin
    print("Paylaşıldı:", pub)

    if not story_url:
        print(f"::warning::{story_file} yok; hikâye paylaşılmadı.")
        return
    try:
        story = publish(uid, token, {"media_type": "STORIES", "video_url": story_url})
    except (Exception, SystemExit) as e:
        print(f"::warning::Reels paylaşıldı ama hikâye paylaşılamadı: {e}")
        return
    record["ig_story_id"] = story.get("id")
    save(posted)
    print("Hikâye paylaşıldı:", story)


if __name__ == "__main__":
    main()
