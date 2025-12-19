# AlexAI Greeting Cards - Setup Guide

A professional greeting card creation and sharing platform powered by AI (Seedream-4.5) with Cloudflare R2 storage for persistence.

## Features

- 🎨 **10 Beautiful Templates**: Birthday, Christmas, Halloween, Easter, Valentine's Day, Thanksgiving, New Year, Graduation, Wedding, Thank You
- 🤖 **AI-Powered Generation**: Uses Seedream-4.5 for 4K high-quality image generation
- 💎 **Professional Watermarking**: Automatic "AlexAI Cards" watermark in elegant font
- ☁️ **Cloud Storage**: Cloudflare R2 for reliable, persistent storage
- 🔗 **Shareable Links**: Generate unique URLs to share cards with anyone
- 📥 **High-Res Downloads**: Download cards in full 4K resolution

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Replicate API Account** - Sign up at [replicate.com](https://replicate.com)
3. **Cloudflare Account** with R2 enabled - Sign up at [cloudflare.com](https://cloudflare.com)

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Replicate API

1. Go to [replicate.com](https://replicate.com)
2. Sign up or log in
3. Navigate to your account settings
4. Copy your API token
5. Set it as an environment variable:

```bash
export REPLICATE_API_TOKEN=r8_your_token_here
```

For Windows (Command Prompt):
```cmd
set REPLICATE_API_TOKEN=r8_your_token_here
```

For Windows (PowerShell):
```powershell
$env:REPLICATE_API_TOKEN="r8_your_token_here"
```

### Step 3: Set Up Cloudflare R2

#### Create R2 Bucket

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **R2 Object Storage**
3. Click **Create Bucket**
4. Name your bucket (e.g., `greeting-cards`)
5. Note your Account ID (found in the R2 dashboard URL or settings)

#### Generate API Tokens

1. In R2 dashboard, click **Manage R2 API Tokens**
2. Click **Create API Token**
3. Give it a name (e.g., "Greeting Cards App")
4. Set permissions to **Edit** (allows read and write)
5. Set expiry (recommend 1 year)
6. Click **Create API Token**
7. Save the following:
   - Access Key ID
   - Secret Access Key
   - Account ID

⚠️ **Important**: Store these credentials securely and never commit them to version control!

#### Set Environment Variables

```bash
export R2_ACCOUNT_ID=your_account_id
export R2_ACCESS_KEY_ID=your_access_key_id
export R2_SECRET_ACCESS_KEY=your_secret_access_key
export R2_BUCKET_NAME=greeting-cards
```

For Windows (Command Prompt):
```cmd
set R2_ACCOUNT_ID=your_account_id
set R2_ACCESS_KEY_ID=your_access_key_id
set R2_SECRET_ACCESS_KEY=your_secret_access_key
set R2_BUCKET_NAME=greeting-cards
```

#### Configure Public Access (Optional)

To enable direct public URLs:

1. In your R2 bucket settings, enable **Public Access**
2. Set up a custom domain or use R2.dev subdomain
3. Set the public URL:

```bash
export R2_PUBLIC_URL=https://your-bucket.r2.dev
```

### Step 4: Create Environment File (Recommended)

Create a `.env` file in your project root:

```env
REPLICATE_API_TOKEN=r8_your_token_here
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET_NAME=greeting-cards
R2_PUBLIC_URL=https://your-bucket.r2.dev
APP_URL=http://localhost:7860
```

Then install python-dotenv and load it:

```bash
pip install python-dotenv
```

Add to the top of your app:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Running the Application

### Development Mode

```bash
python app.py
```

The app will be available at `http://localhost:7860`

### With Share Link (Public Access)

```bash
python app.py
```

Gradio will automatically generate a shareable link (e.g., `https://xxxxx.gradio.live`)

### Production Deployment

#### Option 1: Hugging Face Spaces

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Upload `app.py` and `requirements.txt`
3. Add your environment variables in Space settings
4. Space will automatically deploy

#### Option 2: Custom Server

For production deployment on your own server:

1. Use a production WSGI server (e.g., Gunicorn)
2. Set up reverse proxy (Nginx)
3. Configure SSL certificates
4. Set environment variables in server config

Example nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Usage Guide

### Creating a Card

1. **Select Template**: Choose from 10 occasion-specific templates
2. **Add Recipient**: Enter the recipient's name (optional)
3. **Personal Message**: Write a custom message (optional)
4. **Date**: Add a special date (optional)
5. **Additional Details**: Specify any custom elements you'd like (optional)
6. **Generate**: Click "Generate Card" and wait 10-20 seconds
7. **Download or Share**: Download the high-res image or copy the shareable link

### Sharing Cards

Each generated card gets:
- **Unique ID**: A UUID for tracking
- **Public URL**: Direct link to the image on R2
- **Shareable Link**: App URL with card ID for viewing
- **Metadata**: Stored in R2 for retrieval

Share the link with anyone - they can view and download the card without needing the app.

## Architecture & Best Practices

### Data Flow

1. **User Input** → Gradio Interface
2. **Template Selection** → Prompt Engineering
3. **Replicate API** → Seedream-4.5 Generation (4K)
4. **Local Processing** → Watermark Addition (PIL)
5. **R2 Upload** → Cloud Storage (boto3)
6. **Metadata Storage** → JSON in R2
7. **Share Link** → Generated URL

### Best Practices Implemented

#### Image Generation
- **High Resolution**: 4K (3840x2160) for print quality
- **Aspect Ratio**: 16:9 for versatility
- **Quality**: JPEG 95% quality for optimal size/quality ratio

#### Watermarking
- **Elegant Font**: Tries multiple elegant fonts with fallback
- **Smart Positioning**: Bottom-right with 2% margin
- **Semi-Transparent**: White with 60% opacity
- **Responsive Size**: Scaled to 2.5% of image height

#### Storage
- **S3-Compatible API**: Uses boto3 with R2 endpoint
- **Proper Content-Type**: Set for correct browser handling
- **Cache Headers**: 1-year cache for performance
- **Organized Structure**: `cards/` and `metadata/` prefixes

#### Security
- **Environment Variables**: Never hardcode credentials
- **Validation**: Input sanitization and error handling
- **Rate Limiting**: Relies on Replicate's built-in limits
- **Public Access**: Optional - can keep buckets private

#### Performance
- **Async Processing**: Gradio handles concurrent requests
- **Efficient Uploads**: Direct boto3 file streaming
- **Metadata Separation**: JSON metadata for quick lookups
- **CDN-Ready**: R2 public URLs work with Cloudflare CDN

## Troubleshooting

### "Error initializing R2 client"
- Check that all R2 environment variables are set correctly
- Verify account ID, access key, and secret key
- Ensure R2 is enabled on your Cloudflare account

### "Replicate API error"
- Verify your `REPLICATE_API_TOKEN` is set correctly
- Check your Replicate account has sufficient credits
- Ensure the token hasn't expired

### "Watermark not applying"
- App will continue without watermark if fonts aren't found
- Install system fonts: `apt-get install fonts-dejavu` (Linux)
- The app includes fallback to default font

### "Cards not persisting"
- Ensure R2 bucket exists and is accessible
- Check bucket permissions allow write operations
- Verify environment variables are loaded

### "Share links not working"
- Set `APP_URL` environment variable to your actual app URL
- For local testing, use `http://localhost:7860`
- For production, use your domain: `https://cards.yourdomain.com`

## Cost Considerations

### Replicate
- Seedream-4.5: ~$0.01-0.02 per image
- Pay-as-you-go pricing
- Estimate: $1-2 per 100 cards

### Cloudflare R2
- Storage: $0.015/GB per month
- Class A Operations (write): $4.50 per million
- Class B Operations (read): $0.36 per million
- Zero egress fees (unlike AWS S3)
- Estimate: ~$1/month for 1000 cards + views

## Customization

### Adding New Templates

Edit the `CARD_TEMPLATES` dictionary in `app.py`:

```python
CARD_TEMPLATES["Mother's Day"] = {
    "prompt": "Your detailed prompt here...",
    "aspect_ratio": "16:9",
    "description": "Brief description"
}
```

### Changing Watermark

Modify the `add_watermark()` function:
- Change text
- Adjust position
- Modify opacity
- Use different fonts

### Custom Styling

Add CSS in the Gradio Blocks `css` parameter:

```python
with gr.Blocks(css="""
    .custom-style { background: #fff; }
""") as demo:
    ...
```

## Support & Contributing

For issues, questions, or contributions:
1. Check existing documentation
2. Review troubleshooting section
3. Open an issue with details

## License

This project is provided as-is for demonstration purposes.

## Credits

- **AI Model**: Seedream-4.5 by ByteDance
- **Framework**: Gradio
- **Storage**: Cloudflare R2
- **Image Processing**: Pillow (PIL)

---

**Created with ❤️ by AlexAI**