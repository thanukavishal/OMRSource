# Web App

This project has a React frontend and a Python API around the OMR pipeline.

## Run the API

```powershell
python server.py
```

The API runs at `http://127.0.0.1:8000`.

## Run the React App

```powershell
npm.cmd install
npm.cmd run dev
```

The web app runs at `http://127.0.0.1:5173`.

## Workflow

1. Upload a PNG, JPG, or JPEG sheet music image.
2. The Python image processing pipeline detects notes and generates preview images.
3. The React page shows the detected notes and summary metrics.
4. Download the generated `converted_music.mid` file from the actions panel.
