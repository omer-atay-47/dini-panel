"""Günlük Instagram Reels paylaşımı (GitHub Actions ile çalışır, yalnızca standart kütüphane).

Mantık:
  - schedule.json içinden bugünün tarihine ait ve henüz paylaşılmamış videoyu bulur.
  - Video, GitHub Pages adresinden (herkese açık https bağlantısı) Instagram'a verilir.
  - Paylaşılanlar posted.json içine yazılır; aynı video iki kez paylaşılmaz.

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
    if dry:
        print("DRY_RUN: paylaşım yapılmadı.\nAçıklama:\n" + caption)
        return

    uid, token = os.environ["IG_USER_ID"], os.environ["IG_TOKEN"]
    c = call("POST", f"{API}/{uid}/media", {"media_type": "REELS", "video_url": video_url, "caption": caption, "share_to_feed": "true", "access_token": token})
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
    pub = call("POST", f"{API}/{uid}/media_publish", {"creation_id": cid, "access_token": token})
    posted.append({"id": item["id"], "tarih": today, "ig_media_id": pub.get("id")})
    with open(os.path.join(ROOT, "otomasyon/posted.json"), "w", encoding="utf-8") as f:
        json.dump(posted, f, ensure_ascii=False, indent=1)
    print("Paylaşıldı:", pub)


if __name__ == "__main__":
    main()
