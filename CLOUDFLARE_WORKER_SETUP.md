# Cloudflare Worker Setup Guide

This guide explains how to deploy the Cloudflare Worker for public card viewing.

## Why Use a Cloudflare Worker?

The Cloudflare Worker provides:
- **Public Card Viewing**: Share cards via simple URLs
- **Fast Global Access**: Cloudflare's edge network
- **Seamless R2 Integration**: Direct access to card storage
- **Beautiful UI**: Custom HTML pages for card viewing
- **API Endpoints**: JSON API for card metadata

## Prerequisites

1. **Cloudflare Account** with R2 enabled
2. **Wrangler CLI** installed
3. **R2 Bucket** created (from main app setup)

## Installation Steps

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

Or with npm in your project:
```bash
npm install --save-dev wrangler
```

### 2. Authenticate Wrangler

```bash
wrangler login
```

This opens a browser to authenticate with Cloudflare.

### 3. Verify R2 Bucket

Check that your bucket exists:
```bash
wrangler r2 bucket list
```

You should see your `greeting-cards` bucket.

### 4. Update Configuration

Edit `wrangler.toml` and update:
```toml
[[r2_buckets]]
binding = "CARDS_BUCKET"
bucket_name = "greeting-cards"  # Your actual bucket name
```

### 5. Deploy Worker

```bash
wrangler deploy
```

Wrangler will:
1. Upload your worker code
2. Bind it to your R2 bucket
3. Provide a URL like: `https://alexai-cards-viewer.your-subdomain.workers.dev`

## Testing

### Test Homepage
```bash
curl https://your-worker-url.workers.dev/
```

### Test Card Viewing
```bash
curl https://your-worker-url.workers.dev/view?id=CARD_ID
```

### Test Image Access
```bash
curl https://your-worker-url.workers.dev/cards/CARD_ID.jpg
```

### Test API
```bash
curl https://your-worker-url.workers.dev/api/card/CARD_ID
```

## Updating the Main App

Once deployed, update your main app's `APP_URL` environment variable:

```bash
export APP_URL=https://your-worker-url.workers.dev
```

Or in `.env`:
```env
APP_URL=https://your-worker-url.workers.dev
```

Now when users generate cards, the shareable links will point to your Cloudflare Worker!

## Custom Domain Setup (Optional)

### 1. Add Custom Domain in Cloudflare

1. Go to Cloudflare Dashboard
2. Select your worker
3. Click "Settings" → "Triggers"
4. Click "Add Custom Domain"
5. Enter: `cards.yourdomain.com`
6. Cloudflare will automatically handle DNS

### 2. Update wrangler.toml

```toml
routes = [
  { pattern = "cards.yourdomain.com/*", zone_name = "yourdomain.com" }
]
```

### 3. Redeploy

```bash
wrangler deploy
```

### 4. Update App URL

```env
APP_URL=https://cards.yourdomain.com
```

## Worker Routes Explained

### `/` (Homepage)
- Shows app information
- Lists features
- Provides usage instructions

### `/view?id=CARD_ID` (Card Viewer)
- Displays card in beautiful UI
- Shows metadata (recipient, message, date)
- Provides download button
- Share functionality

### `/cards/CARD_ID.jpg` (Direct Image)
- Serves the card image directly
- Cached for 1 year
- Works in Open Graph previews

### `/api/card/CARD_ID` (API)
- Returns card metadata as JSON
- Useful for programmatic access
- CORS enabled

## Architecture

```
User Request
    ↓
Cloudflare Worker (Edge)
    ↓
R2 Bucket (Storage)
    ↓
Response (HTML/JSON/Image)
```

Benefits:
- **Fast**: Served from Cloudflare edge
- **Scalable**: Handles unlimited traffic
- **Cheap**: Free tier covers most usage
- **Secure**: No exposed credentials

## Monitoring

### View Logs (Real-time)
```bash
wrangler tail
```

### View Analytics
1. Go to Cloudflare Dashboard
2. Select your worker
3. View "Analytics" tab

Metrics available:
- Requests per second
- Success rate
- Errors
- CPU time
- Bandwidth

## Development Workflow

### Local Development
```bash
wrangler dev
```

This starts a local server at `http://localhost:8787`

### Test with Local R2
```bash
wrangler dev --local
```

### Preview Deployment
```bash
wrangler deploy --env dev
```

This deploys to a separate dev environment.

## Troubleshooting

### "Error: binding not found"
- Check `wrangler.toml` has correct bucket name
- Verify R2 bucket exists: `wrangler r2 bucket list`
- Ensure you're authenticated: `wrangler whoami`

### "404 Card Not Found"
- Verify card exists in R2: `wrangler r2 object list greeting-cards`
- Check card ID is correct
- Ensure metadata was saved during card creation

### "CORS errors"
- Worker includes CORS headers by default
- Check browser console for specific error
- Verify worker is deployed correctly

### Images not loading
- Check image exists: `wrangler r2 object get greeting-cards cards/CARD_ID.jpg`
- Verify content type is set correctly
- Clear browser cache

## Cost Estimates

Cloudflare Workers Free Tier:
- **100,000 requests/day** for free
- **10ms CPU time per request**
- **Unlimited bandwidth**

R2 Free Tier:
- **10 GB storage** for free
- **1 million Class B operations** (reads) per month

Typical costs for 10,000 cards/month:
- Storage: ~$0-0.15
- Reads: Free (within limits)
- Workers: Free (within limits)

**Total: $0-0.15/month for most use cases**

## Security Best Practices

1. **Never expose R2 credentials in worker code**
   - Worker uses bindings, not credentials
   
2. **Validate input**
   - Card IDs should be UUIDs
   - Sanitize any user input
   
3. **Rate limiting** (optional)
   - Add rate limiting for API endpoints
   - Use Cloudflare's built-in DDoS protection

4. **Access control** (optional)
   - Add authentication for sensitive cards
   - Use Cloudflare Access for team access

## Advanced Features

### Add Caching Layer

```javascript
// In worker.js, add caching
const cache = caches.default;
const cacheKey = new Request(url.toString(), request);
const cachedResponse = await cache.match(cacheKey);

if (cachedResponse) {
  return cachedResponse;
}

// ... generate response ...

await cache.put(cacheKey, response.clone());
return response;
```

### Add Analytics

```javascript
// Track card views
await env.ANALYTICS.writeDataPoint({
  'blobs': ['card-view'],
  'doubles': [1],
  'indexes': [cardId]
});
```

### Add Authentication

```javascript
// Require token for certain routes
const token = request.headers.get('Authorization');
if (!isValidToken(token)) {
  return new Response('Unauthorized', { status: 401 });
}
```

## Next Steps

1. ✅ Deploy worker
2. ✅ Test all routes
3. ✅ Update main app URL
4. ✅ Generate test card
5. ✅ Share with friends!

Optional:
- 🎨 Customize HTML templates
- 🔒 Add authentication
- 📊 Set up analytics
- 🌐 Add custom domain

## Support

For issues:
1. Check worker logs: `wrangler tail`
2. Review R2 bucket contents
3. Test locally: `wrangler dev`
4. Check Cloudflare status page

## Resources

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [R2 Docs](https://developers.cloudflare.com/r2/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)

---

**Happy deploying! 🚀**