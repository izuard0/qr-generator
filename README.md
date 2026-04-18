# QR Code Generator

Generate QR codes with a custom logo/image, deployable via Docker on Coolify.

## Features

- Input URL or text to encode
- Upload custom logo — centered on the QR code automatically
- Choose QR color and background color
- Watermark `make yours at qr.ifuntanhub.dev` embedded in every output image
- Download result as PNG
- Copy to clipboard

## Tech Stack

| Layer     | Tech                          |
|-----------|-------------------------------|
| Backend   | Python · Flask · qrcode · Pillow |
| Frontend  | HTML · Bootstrap 4 · Vanilla JS |
| Server    | Gunicorn                      |
| Deploy    | Docker · Coolify              |

## Project Structure

```
qr-generator/
├── app.py              # Flask app — POST /generate endpoint
├── requirements.txt    # Python dependencies
├── Dockerfile          # python:3.12-slim + gunicorn
├── docker-compose.yml  # local dev
└── templates/
    └── index.html      # one-page frontend
```

## Running Locally

**With Docker (recommended):**
```bash
docker compose up --build
```
Open [http://localhost:5000](http://localhost:5000)

**Without Docker:**
```bash
pip install -r requirements.txt
python app.py
```

## API

### `POST /generate`

| Field      | Type   | Required | Description                  |
|------------|--------|----------|------------------------------|
| `url`      | string | yes      | URL or text to encode        |
| `qr_color` | string | no       | Hex color for QR dots (default `#000000`) |
| `qr_bg`    | string | no       | Hex color for background (default `#ffffff`) |
| `logo`     | file   | no       | Image file to overlay in center |

Returns a `image/png` file.

## Environment

No environment variables required. The app runs on port `5000`.
