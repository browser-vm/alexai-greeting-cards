# AlexAI Greeting Cards - Quick Start

Get your greeting card app running in 5 minutes!

## 1. Install Dependencies (1 min)

```bash
pip install gradio replicate Pillow boto3 requests python-dotenv
```

## 2. Get API Keys (2 min)

### Replicate API
1. Go to [replicate.com](https://replicate.com)
2. Sign up/login
3. Get your API token from account settings

### Cloudflare R2
1. Go to [dash.cloudflare.com](https://dash.cloudflare.com)
2. Navigate to R2 Object Storage
3. Create a bucket named `greeting-cards`
4. Create API token with Edit permissions
5. Note your: Account ID, Access Key ID, Secret Access Key

## 3. Configure Environment (1 min)

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
REPLICATE_API_TOKEN=r8_xxxxx
R2_ACCOUNT_ID=xxxxx
R2_ACCESS_KEY_ID=xxxxx
R2_SECRET_ACCESS_KEY=xxxxx
R2_BUCKET_NAME=greeting-cards
```

## 4. Run the App (30 seconds)

```bash
python app.py
```

Open browser to: `http://localhost:7860`

## 5. Create Your First Card! (30 seconds)

1. Select a template (e.g., "Birthday")
2. Add a recipient name
3. Add a message
4. Click "Generate Card"
5. Wait 15-20 seconds
6. Download or share!

## Tips

- **Share Mode**: The app creates a public link automatically
- **Templates**: Try all 10 templates for different occasions
- **Customization**: Add specific details for unique cards
- **High-Res**: All cards are generated in 4K quality
- **Watermark**: "AlexAI Cards" is automatically added

## Common Issues

**"R2 client not initialized"**
- Check your `.env` file has all R2 credentials
- Ensure R2 is enabled in your Cloudflare account

**"Replicate API error"**
- Verify your `REPLICATE_API_TOKEN` is correct
- Check you have credits on Replicate

**Watermark not showing**
- This is okay - app works without watermark
- Install system fonts for better results

## What's Next?

1. **Customize**: Edit `CARD_TEMPLATES` to add new templates
2. **Brand**: Change watermark text in `add_watermark()`
3. **Deploy**: Host on Hugging Face Spaces or your server
4. **Share**: Generate cards and share with friends!

## Need Help?

Check the full README.md for:
- Detailed setup instructions
- Architecture explanation
- Troubleshooting guide
- Production deployment tips
- Cost estimates

---

**Happy card making! 🎨**