"""Her video için hikâye videosu üretir: videos/story/<id>.mp4 (1080x1920).

Hikâye, videonun ilk saniyelerini çerçeve içinde gösterir; üstte "YENİ VİDEO",
altta "Tamamı profilimizde" yazar. Bilgisayarda çalıştırılır (ffmpeg + Pillow gerekir):

    python otomasyon/hikaye.py            # eksik olanları üretir
    python otomasyon/hikaye.py --hepsi    # hepsini yeniden üretir

Süre, schedule.json içindeki "hikaye_sn" alanından alınır (yoksa 10 saniye).
Yeni video eklenince bu betik çalıştırılıp çıkan dosya GitHub'a yüklenmelidir.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = r"C:\Windows\Fonts"
HANDLE = "@hikmet.kandili"
GOLD = (232, 193, 103, 255)
X, Y, W, H = 205, 380, 670, 1190  # küçük videonun yeri; üst ve alt Instagram arayüzüne boş kalır


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def overlay(path):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([X - 5, Y - 5, X + W + 4, Y + H + 4], radius=10, outline=GOLD, width=5)
    d.rounded_rectangle([X - 17, Y - 17, X + W + 16, Y + H + 16], radius=18, outline=GOLD[:3] + (120,), width=2)
    d.rounded_rectangle([300, 245, 780, 335], radius=45, fill=(138, 23, 48, 255), outline=GOLD, width=3)
    d.text((540, 289), "YENİ VİDEO", font=font("segoeuib.ttf", 46), fill="white", anchor="mm")
    d.rounded_rectangle([170, 1605, 910, 1755], radius=26, fill=(5, 9, 24, 225), outline=GOLD, width=2)
    d.text((540, 1652), "Tamamı profilimizde", font=font("georgiab.ttf", 52), fill=(251, 239, 207, 255), anchor="mm")
    d.text((540, 1717), HANDLE, font=font("segoeuib.ttf", 34), fill=GOLD, anchor="mm")
    im.save(path)


def make(vid, seconds, png):
    src = os.path.join(ROOT, "videos", f"{vid}.mp4")
    out = os.path.join(ROOT, "videos", "story", f"{vid}.mp4")
    graph = (
        "[0:v]split[a][b];"
        "[a]scale=270:480,gblur=sigma=7,scale=1080:1920,eq=brightness=-0.16[bg];"
        f"[b]scale={W}:{H}[fg];[bg][fg]overlay={X}:{Y}[v1];"
        "[v1][1:v]overlay=0:0,format=yuv420p[v];"
        f"[0:a]afade=t=out:st={seconds - 0.4:.2f}:d=0.4[a_out]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", src, "-i", png,
        "-filter_complex", graph, "-map", "[v]", "-map", "[a_out]", "-t", f"{seconds:.2f}",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.2", "-preset", "slow", "-crf", "23",
        "-maxrate", "6M", "-bufsize", "12M", "-r", "30", "-g", "60",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart", "-use_editlist", "0", out,
    ], check=True)
    print("hazır:", os.path.relpath(out, ROOT), f"{seconds} sn")


def main():
    data_path = os.path.join(ROOT, "data.json")
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    videos = data["videolar"]
    with open(os.path.join(ROOT, "otomasyon", "schedule.json"), encoding="utf-8") as f:
        seconds = {s["id"]: s.get("hikaye_sn", 10) for s in json.load(f)}
    os.makedirs(os.path.join(ROOT, "videos", "story"), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        png = os.path.join(tmp, "overlay.png")
        overlay(png)
        for v in videos:
            out = os.path.join(ROOT, "videos", "story", f"{v['id']}.mp4")
            if "--hepsi" in sys.argv or not os.path.exists(out):
                make(v["id"], seconds.get(v["id"], 10), png)
            v["hikaye"] = f"videos/story/{v['id']}.mp4"  # panel bu alana bakar
    with open(data_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
