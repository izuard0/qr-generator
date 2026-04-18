from flask import Flask, request, send_file, render_template
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io
import os

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

WATERMARK_TEXT = "make yours at qr.ifuntanhub.dev"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    url = request.form.get("url", "").strip()
    if not url:
        return {"error": "URL is required"}, 400

    qr_color = request.form.get("qr_color", "#000000")
    qr_bg    = request.form.get("qr_bg", "#ffffff")
    logo_file = request.files.get("logo")

    # ── Generate QR ────────────────────────────────────────────
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img_qr = qr.make_image(
        fill_color=qr_color,
        back_color=qr_bg,
    ).convert("RGBA")

    qr_w, qr_h = img_qr.size

    # ── Overlay logo ────────────────────────────────────────────
    if logo_file:
        logo = Image.open(logo_file.stream).convert("RGBA")
        logo_max = qr_w // 4
        lw, lh = logo.size
        if lw > logo_max or lh > logo_max:
            if lw >= lh:
                logo = logo.resize(
                    (logo_max, int(logo_max * lh / lw)), Image.LANCZOS
                )
            else:
                logo = logo.resize(
                    (int(logo_max * lw / lh), logo_max), Image.LANCZOS
                )

        lw, lh = logo.size
        pad = 10
        bg_box = Image.new(
            "RGBA",
            (lw + pad * 2, lh + pad * 2),
            _hex_to_rgba(qr_bg),
        )
        paste_x = (qr_w - lw) // 2
        paste_y = (qr_h - lh) // 2
        img_qr.paste(bg_box, (paste_x - pad, paste_y - pad), bg_box)
        img_qr.paste(logo, (paste_x, paste_y), logo)

    # ── Watermark strip ─────────────────────────────────────────
    strip_h = 40
    final = Image.new("RGBA", (qr_w, qr_h + strip_h), (63, 66, 87, 255))
    final.paste(img_qr, (0, 0))

    draw = ImageDraw.Draw(final)
    font = _load_font(13)
    bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (qr_w - text_w) // 2
    text_y = qr_h + (strip_h - (bbox[3] - bbox[1])) // 2
    draw.text((text_x, text_y), WATERMARK_TEXT, fill=(255, 255, 255, 140), font=font)

    # ── Return PNG ──────────────────────────────────────────────
    buf = io.BytesIO()
    final.convert("RGB").save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return send_file(buf, mimetype="image/png", download_name="qr-code.png")


# ── Helpers ─────────────────────────────────────────────────────

def _hex_to_rgba(hex_color: str, alpha: int = 255):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (r, g, b, alpha)


def _load_font(size: int):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
