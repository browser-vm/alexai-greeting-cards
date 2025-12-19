/**
 * Cloudflare Worker for AlexAI Greeting Cards
 * 
 * This worker serves as a public endpoint for viewing and downloading cards
 * It fetches card images and metadata from R2 storage
 * 
 * Deploy this to Cloudflare Workers for a production-ready card viewing system
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS headers for API requests
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, HEAD, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Route: View card page
    if (path.startsWith('/view')) {
      const cardId = url.searchParams.get('id');
      
      if (!cardId) {
        return new Response('Card ID required', { 
          status: 400,
          headers: { 'Content-Type': 'text/plain' }
        });
      }

      try {
        // Fetch card metadata from R2
        const metadataKey = `metadata/${cardId}.json`;
        const metadataObj = await env.CARDS_BUCKET.get(metadataKey);
        
        if (!metadataObj) {
          return new Response('Card not found', { 
            status: 404,
            headers: { 'Content-Type': 'text/plain' }
          });
        }

        const metadata = await metadataObj.json();
        
        // Fetch card image from R2
        const imageKey = `cards/${cardId}.jpg`;
        const imageObj = await env.CARDS_BUCKET.get(imageKey);
        
        if (!imageObj) {
          return new Response('Card image not found', { 
            status: 404,
            headers: { 'Content-Type': 'text/plain' }
          });
        }

        // Generate HTML page for viewing the card
        const html = generateCardViewPage(metadata, cardId);
        
        return new Response(html, {
          headers: {
            'Content-Type': 'text/html',
            ...corsHeaders
          }
        });

      } catch (error) {
        return new Response(`Error loading card: ${error.message}`, { 
          status: 500,
          headers: { 'Content-Type': 'text/plain' }
        });
      }
    }

    // Route: Get card image
    if (path.startsWith('/cards/')) {
      const cardId = path.replace('/cards/', '').replace('.jpg', '');
      
      try {
        const imageKey = `cards/${cardId}.jpg`;
        const imageObj = await env.CARDS_BUCKET.get(imageKey);
        
        if (!imageObj) {
          return new Response('Image not found', { 
            status: 404,
            headers: { 'Content-Type': 'text/plain' }
          });
        }

        return new Response(imageObj.body, {
          headers: {
            'Content-Type': 'image/jpeg',
            'Cache-Control': 'public, max-age=31536000',
            ...corsHeaders
          }
        });

      } catch (error) {
        return new Response(`Error loading image: ${error.message}`, { 
          status: 500,
          headers: { 'Content-Type': 'text/plain' }
        });
      }
    }

    // Route: Get card metadata API
    if (path.startsWith('/api/card/')) {
      const cardId = path.replace('/api/card/', '');
      
      try {
        const metadataKey = `metadata/${cardId}.json`;
        const metadataObj = await env.CARDS_BUCKET.get(metadataKey);
        
        if (!metadataObj) {
          return new Response(JSON.stringify({ error: 'Card not found' }), { 
            status: 404,
            headers: { 
              'Content-Type': 'application/json',
              ...corsHeaders
            }
          });
        }

        const metadata = await metadataObj.json();
        
        return new Response(JSON.stringify(metadata), {
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        });

      } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), { 
          status: 500,
          headers: { 
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        });
      }
    }

    // Default: Homepage
    return new Response(generateHomePage(), {
      headers: {
        'Content-Type': 'text/html',
        ...corsHeaders
      }
    });
  }
};

/**
 * Generate HTML for viewing a card
 */
function generateCardViewPage(metadata, cardId) {
  const imageUrl = `/cards/${cardId}.jpg`;
  const downloadUrl = imageUrl;
  
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${metadata.template} Card - AlexAI Cards</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 1200px;
            width: 100%;
            padding: 40px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .card-image {
            width: 100%;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .card-info {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .info-row:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        
        .info-label {
            font-weight: 600;
            color: #495057;
        }
        
        .info-value {
            color: #6c757d;
        }
        
        .actions {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .btn {
            flex: 1;
            min-width: 200px;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-secondary {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #6c757d;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
            
            .actions {
                flex-direction: column;
            }
            
            .btn {
                min-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 ${metadata.template} Card</h1>
            <p>Created with AlexAI Cards</p>
        </div>
        
        <img src="${imageUrl}" alt="Greeting Card" class="card-image" />
        
        <div class="card-info">
            ${metadata.recipient ? `
            <div class="info-row">
                <span class="info-label">For:</span>
                <span class="info-value">${escapeHtml(metadata.recipient)}</span>
            </div>
            ` : ''}
            
            ${metadata.message ? `
            <div class="info-row">
                <span class="info-label">Message:</span>
                <span class="info-value">${escapeHtml(metadata.message)}</span>
            </div>
            ` : ''}
            
            ${metadata.date ? `
            <div class="info-row">
                <span class="info-label">Date:</span>
                <span class="info-value">${escapeHtml(metadata.date)}</span>
            </div>
            ` : ''}
            
            <div class="info-row">
                <span class="info-label">Template:</span>
                <span class="info-value">${escapeHtml(metadata.template)}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">Created:</span>
                <span class="info-value">${new Date(metadata.created_at).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}</span>
            </div>
        </div>
        
        <div class="actions">
            <a href="${downloadUrl}" download="alexai-card-${cardId}.jpg" class="btn btn-primary">
                📥 Download Card
            </a>
            <button onclick="shareCard()" class="btn btn-secondary">
                🔗 Share Link
            </button>
        </div>
        
        <div class="footer">
            <p>Created with ❤️ by AlexAI Cards</p>
            <p style="margin-top: 10px;">Powered by Seedream-4.5 • Stored on Cloudflare R2</p>
        </div>
    </div>
    
    <script>
        function shareCard() {
            const url = window.location.href;
            if (navigator.share) {
                navigator.share({
                    title: '${metadata.template} Card',
                    text: 'Check out this greeting card!',
                    url: url
                }).catch(err => copyToClipboard(url));
            } else {
                copyToClipboard(url);
            }
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('Link copied to clipboard!');
            }).catch(() => {
                prompt('Copy this link:', text);
            });
        }
    </script>
</body>
</html>
  `;
}

/**
 * Generate homepage HTML
 */
function generateHomePage() {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AlexAI Greeting Cards</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 60px 40px;
            text-align: center;
        }
        
        h1 {
            font-size: 3em;
            color: #333;
            margin-bottom: 20px;
        }
        
        p {
            font-size: 1.2em;
            color: #666;
            margin-bottom: 40px;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .feature {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .feature-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .feature h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .feature p {
            font-size: 0.9em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 AlexAI Greeting Cards</h1>
        <p>Create beautiful, personalized greeting cards powered by AI</p>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">🎉</div>
                <h3>10 Templates</h3>
                <p>Birthday, Christmas, Halloween, and more</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🤖</div>
                <h3>AI-Powered</h3>
                <p>High-quality 4K image generation</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🔗</div>
                <h3>Easy Sharing</h3>
                <p>Share links with anyone</p>
            </div>
        </div>
        
        <p>To view a card, visit: <code>/view?id=CARD_ID</code></p>
    </div>
</body>
</html>
  `;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}