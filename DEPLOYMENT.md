# ImageGuard Render Deployment

ImageGuard is a Streamlit Python web service. This deployment uses Render's native Python runtime; it does not need Docker, ExifTool, application secrets, or a database.

## Before deploying

1. Push the project to a GitHub repository. The repository root must contain `app.py`, `requirements.txt`, `render.yaml`, `.python-version`, and `run_streamlit.py`.
2. Confirm that `.env`, virtual environments, generated reports, and caches are not committed. The project `.gitignore` excludes them.
3. No application environment variables need to be entered manually. Render provides `PORT`; the launcher binds Streamlit to `0.0.0.0` and uses that port. Python 3.11.9 is selected by `.python-version`.

## Create the Render service

The repository includes a Blueprint in `render.yaml`. In Render:

1. Choose **New → Blueprint**.
2. Connect the GitHub repository containing ImageGuard.
3. Review and create the `imageguard-forensics` web service.
4. Wait for the build and deploy to finish. Render will assign a public HTTPS URL.

The service settings are:

| Setting | Value |
| --- | --- |
| Service type | Web Service |
| Runtime | Python 3 |
| Root Directory | Leave blank (repository root) |
| Python version | 3.11.9 (`.python-version`) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python run_streamlit.py` |
| Health check path | `/_stcore/health` |
| Environment variables | None to add manually; Render supplies `PORT` |

The launcher defaults to port `10000` for local runs when `PORT` is unset. It validates the port value and starts Streamlit without invoking a shell. Normal Windows development remains `streamlit run app.py`.

## Verify the deployment

1. Open the `onrender.com` URL shown on the service page.
2. Upload a supported JPG, PNG, WEBP, or TIFF image under 25 MB and 20 million pixels.
3. Confirm the image overview and forensic analysis pages load.
4. Open **Generate PDF Forensic Report**, compile the report, and download the PDF.
5. Check Render's deploy logs if startup or the health check fails.

## Storage and service limits

- Uploaded image bytes are processed in memory; uploads are not saved as permanent files.
- Generated report PDFs are written under the project `reports/` directory so Streamlit can offer them for download. Render's default filesystem is ephemeral, so reports are not durable across redeploys or instance replacement.
- Image analysis and PDF rendering use CPU and memory. The app limits uploads to 25 MB and decoded images to 20 million pixels. Larger images must be reduced before upload.
- Free web services can spin down after inactivity and may take longer to respond on the next visit. Processing speed and capacity depend on the selected Render instance.
- ImageGuard produces heuristic forensic indicators, not definitive proof that an image is authentic or manipulated.

## Troubleshooting

- **Build cannot import OpenCV:** confirm the build ran `pip install -r requirements.txt`; this project uses `opencv-python-headless` for server environments.
- **Service fails to bind or health check times out:** confirm the start command is `python run_streamlit.py`. Do not set a fixed production port; Render provides `PORT`.
- **Upload rejected:** supported formats are JPG/JPEG, PNG, WEBP, and TIFF. The upload must be no larger than 25 MB or 20 million decoded pixels.
- **Report generation fails:** inspect the service logs and available memory. Reports are generated on demand and delivered through the download button.
- **Need local sample images:** run `python create_sample_data.py`; sample data is optional and is not required for the uploaded-image workflow.
