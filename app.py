import gradio as gr
import replicate
import os
from dotenv import load_dotenv
import uuid
import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import boto3
from botocore.client import Config
import json
from urllib.parse import quote

# ===========================
# CONFIGURATION
# ===========================

# Load environment variables
load_dotenv()

# Replicate API (should be set in environment)
# Set REPLICATE_API_TOKEN in your environment

# Cloudflare R2 Configuration
# Set these environment variables:
# R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME
R2_ACCOUNT_ID = os.environ.get("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME", "greeting-cards")
R2_PUBLIC_URL = os.environ.get("R2_PUBLIC_URL", "")  # e.g., https://your-domain.com

# Initialize R2 client
def init_r2_client():
    """Initialize Cloudflare R2 client using boto3"""
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        return None
    
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        return s3_client
    except Exception as e:
        print(f"Error initializing R2 client: {e}")
        return None

# ===========================
# CARD TEMPLATES
# ===========================

CARD_TEMPLATES = {
    "Birthday": {
        "prompt": "A vibrant, celebratory birthday scene with colorful balloons, confetti, and a festive atmosphere. Warm lighting, joyful colors including pink, gold, and blue. Shot in high-quality digital photography style with bokeh effect. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Perfect for birthday celebrations with colorful and festive elements"
    },
    "Christmas": {
        "prompt": "A cozy Christmas scene with decorated pine tree, warm fireplace, snow falling outside window, red and gold ornaments, twinkling lights. Nostalgic winter holiday atmosphere with rich textures and warm color palette. Shot in cinematic film style. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Warm holiday scene with Christmas tree and festive decorations"
    },
    "Halloween": {
        "prompt": "A spooky yet charming Halloween scene with carved pumpkins, autumn leaves, vintage lanterns casting warm orange glow, misty atmosphere. Gothic aesthetic with orange, purple, and black color scheme. Atmospheric fog and dramatic lighting. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Spooky autumn scene with pumpkins and mysterious atmosphere"
    },
    "Easter": {
        "prompt": "A cheerful Easter scene with pastel colors, decorated eggs in basket, spring flowers blooming, soft morning sunlight, meadow setting. Gentle, dreamy photography style with soft focus. Colors: soft pink, lavender, mint green, and cream. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Springtime scene with Easter eggs and blooming flowers"
    },
    "Valentine's Day": {
        "prompt": "A romantic Valentine's Day scene with roses, soft candlelight, elegant table setting, dreamy bokeh lights in background. Rich reds and soft pinks, luxurious and intimate atmosphere. Professional photography with shallow depth of field. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Romantic scene with roses and elegant candlelit setting"
    },
    "Thanksgiving": {
        "prompt": "A warm Thanksgiving scene with harvest table, autumn decorations, pumpkins, golden wheat, warm candles, rustic wooden setting. Rich autumn colors: orange, burgundy, gold, brown. Cozy family gathering atmosphere. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Harvest scene with autumn colors and cozy atmosphere"
    },
    "New Year": {
        "prompt": "An elegant New Year's celebration scene with champagne glasses, fireworks, golden confetti, clock showing midnight, sophisticated party setting. Luxurious color palette: gold, silver, black, deep blue. Celebratory and hopeful atmosphere. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Sophisticated celebration with champagne and fireworks"
    },
    "Graduation": {
        "prompt": "An inspiring graduation scene with cap and diploma, books, achievement symbols, bright future ahead imagery. Colors: traditional academic blue, gold, white. Uplifting and proud atmosphere with professional photography style. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Academic achievement scene with cap and diploma"
    },
    "Wedding": {
        "prompt": "An elegant wedding scene with beautiful floral arrangements, soft romantic lighting, elegant venue details, delicate lace and fabric textures. Soft color palette: ivory, blush pink, champagne, sage green. Dreamy and romantic atmosphere. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Elegant romantic scene with flowers and soft lighting"
    },
    "Thank You": {
        "prompt": "A warm, appreciative scene with elegant flowers in vase, handwritten note aesthetic, natural morning light through window, cozy interior setting. Soft, grateful atmosphere with cream, sage, and gold tones. {recipient} {message} {date} {details}",
        "aspect_ratio": "16:9",
        "description": "Warm scene expressing gratitude with flowers and elegant details"
    }
}

# ===========================
# HELPER FUNCTIONS
# ===========================

def add_watermark(image_path, output_path):
    """Add 'AlexAI Cards' watermark to image in elegant font at bottom right"""
    try:
        # Open image
        img = Image.open(image_path).convert("RGBA")
        
        # Create transparent overlay
        txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Watermark text
        watermark_text = "AlexAI Cards"
        
        # Calculate font size based on image dimensions (2% of image height)
        img_width, img_height = img.size
        font_size = int(img_height * 0.025)
        
        # Try to load an elegant font, fallback to default
        try:
            # Try multiple elegant font options
            font_options = [
                "arial.ttf",
                "times.ttf",
                "Georgia.ttf",
                "/System/Library/Fonts/Supplemental/Georgia.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
            ]
            font = None
            for font_path in font_options:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Get text dimensions using textbbox
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position at bottom right with margin
        margin = int(img_width * 0.02)  # 2% margin
        x = img_width - text_width - margin
        y = img_height - text_height - margin
        
        # Draw watermark with semi-transparency (white with 60% opacity)
        draw.text((x, y), watermark_text, fill=(255, 255, 255, 153), font=font)
        
        # Composite the watermark onto the original image
        watermarked = Image.alpha_composite(img, txt_layer)
        
        # Convert back to RGB and save
        watermarked_rgb = watermarked.convert("RGB")
        watermarked_rgb.save(output_path, "JPEG", quality=95)
        
        return output_path
    except Exception as e:
        print(f"Watermark error: {e}")
        # If watermarking fails, just copy the original
        img = Image.open(image_path)
        img.save(output_path, "JPEG", quality=95)
        return output_path

def upload_to_r2(file_path, card_id):
    """Upload image to Cloudflare R2 and return public URL"""
    s3_client = init_r2_client()
    
    if not s3_client:
        print("R2 client not initialized - storing locally only")
        return None
    
    try:
        # Upload to R2
        object_key = f"cards/{card_id}.jpg"
        
        with open(file_path, 'rb') as f:
            s3_client.upload_fileobj(
                f,
                R2_BUCKET_NAME,
                object_key,
                ExtraArgs={
                    'ContentType': 'image/jpeg',
                    'CacheControl': 'public, max-age=31536000'
                }
            )
        
        # Generate public URL
        if R2_PUBLIC_URL:
            public_url = f"{R2_PUBLIC_URL}/{object_key}"
        else:
            public_url = f"https://{R2_BUCKET_NAME}.r2.cloudflarestorage.com/{object_key}"
        
        return public_url
    except Exception as e:
        print(f"R2 upload error: {e}")
        return None

def save_card_metadata(card_id, metadata):
    """Save card metadata to R2"""
    s3_client = init_r2_client()
    
    if not s3_client:
        return None
    
    try:
        metadata_key = f"metadata/{card_id}.json"
        metadata_json = json.dumps(metadata)
        
        s3_client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=metadata_key,
            Body=metadata_json.encode('utf-8'),
            ContentType='application/json'
        )
        
        return metadata_key
    except Exception as e:
        print(f"Metadata save error: {e}")
        return None

def get_card_metadata(card_id):
    """Retrieve card metadata from R2"""
    s3_client = init_r2_client()
    
    if not s3_client:
        return None
    
    try:
        metadata_key = f"metadata/{card_id}.json"
        response = s3_client.get_object(Bucket=R2_BUCKET_NAME, Key=metadata_key)
        metadata = json.loads(response['Body'].read().decode('utf-8'))
        return metadata
    except Exception as e:
        print(f"Metadata retrieve error: {e}")
        return None

# ===========================
# CARD GENERATION
# ===========================

def generate_greeting_card(
    template_name,
    recipient_name,
    custom_message,
    date_text,
    additional_details
):
    """Generate a greeting card using Seedream-4.5"""
    
    status_messages = []
    
    try:
        status_messages.append("🎨 Preparing card generation...")
        
        # Get template
        template = CARD_TEMPLATES.get(template_name)
        if not template:
            return None, None, "❌ Invalid template selected"
        
        # Build custom text components
        recipient_part = f"The card should be made out to {recipient_name}." if recipient_name else ""
        message_part = f"The card should include the message '{custom_message}'." if custom_message else ""
        date_part = f"The date '{date_text}' should be displayed." if date_text else ""
        details_part = f"Include these elements: {additional_details}." if additional_details else ""
        
        # Format prompt
        prompt = template["prompt"].format(
            recipient=recipient_part,
            message=message_part,
            date=date_part,
            details=details_part
        )
        
        # Clean up extra whitespace
        prompt = " ".join(prompt.split())
        
        status_messages.append("🎨 Generating image with Seedream-4.5...")
        
        # Generate with Replicate
        input_params = {
            "size": "4K",
            "prompt": prompt,
            "aspect_ratio": template["aspect_ratio"]
        }
        
        output = replicate.run(
            "bytedance/seedream-4.5",
            input=input_params
        )
        
        status_messages.append("✅ Image generated successfully!")
        
        # Download image
        # Handle both object with .read() (newer replicate) and URL string (older/other models)
        if hasattr(output[0], 'read'):
            image_data = output[0].read()
            image_url = output[0].url if hasattr(output[0], 'url') else None
        elif isinstance(output[0], str) and output[0].startswith('http'):
            import requests
            image_data = requests.get(output[0]).content
            image_url = output[0]
        else:
            raise ValueError(f"Unexpected output format: {type(output[0])}")
        
        # Generate unique ID
        card_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save original
        original_path = f"/tmp/card_{card_id}_original.jpg"
        with open(original_path, "wb") as f:
            f.write(image_data)
        
        status_messages.append("🎨 Adding watermark...")
        
        # Add watermark
        watermarked_path = f"/tmp/card_{card_id}_watermarked.jpg"
        add_watermark(original_path, watermarked_path)
        
        status_messages.append("☁️ Uploading to cloud storage...")
        
        # Upload to R2
        public_url = upload_to_r2(watermarked_path, card_id)
        
        # Save metadata
        metadata = {
            "card_id": card_id,
            "template": template_name,
            "recipient": recipient_name,
            "message": custom_message,
            "date": date_text,
            "created_at": datetime.now().isoformat(),
            "image_url": public_url
        }
        save_card_metadata(card_id, metadata)
        
        # Generate shareable link
        share_link = f"{os.environ.get('APP_URL', 'http://localhost:7860')}/view?id={card_id}"
        
        status_messages.append("✨ Card created successfully!")
        
        # Return image, share link, and status
        return watermarked_path, share_link, "\n".join(status_messages)
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        status_messages.append(error_msg)
        return None, None, "\n".join(status_messages)

# ===========================
# GRADIO INTERFACE
# ===========================

def create_card_interface():
    """Create the main card generation interface"""
    
    with gr.Blocks(
        title="AlexAI Greeting Cards",
        theme=gr.themes.Soft(primary_hue="rose"),
        css="""
        .main-header {text-align: center; margin-bottom: 2em;}
        .card-preview {border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
        .template-desc {font-size: 0.9em; color: #666; font-style: italic;}
        """
    ) as demo:
        
        # Header
        gr.Markdown(
            """
            # 🎨 AlexAI Greeting Cards
            ### Create beautiful, personalized greeting cards powered by AI
            Generate stunning high-resolution cards for any occasion with custom messages
            """,
            elem_classes="main-header"
        )
        
        with gr.Tabs():
            # ===== CREATE TAB =====
            with gr.Tab("✨ Create Card"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Card Details")
                        
                        template_dropdown = gr.Dropdown(
                            choices=list(CARD_TEMPLATES.keys()),
                            value="Birthday",
                            label="Select Card Template",
                            info="Choose the occasion for your card"
                        )
                        
                        template_description = gr.Markdown(
                            CARD_TEMPLATES["Birthday"]["description"],
                            elem_classes="template-desc"
                        )
                        
                        recipient_input = gr.Textbox(
                            label="Recipient Name",
                            placeholder="e.g., Sarah",
                            info="Who is this card for?"
                        )
                        
                        message_input = gr.Textbox(
                            label="Personal Message",
                            placeholder="e.g., Wishing you a wonderful day filled with joy!",
                            lines=3,
                            info="Your heartfelt message (optional)"
                        )
                        
                        date_input = gr.Textbox(
                            label="Date (Optional)",
                            placeholder="e.g., December 25, 2024",
                            info="Include a special date"
                        )
                        
                        details_input = gr.Textbox(
                            label="Additional Details (Optional)",
                            placeholder="e.g., include balloons and cake",
                            lines=2,
                            info="Any specific elements you'd like to see"
                        )
                        
                        generate_btn = gr.Button(
                            "🎨 Generate Card",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Generated Card")
                        
                        status_output = gr.Textbox(
                            label="Status",
                            lines=6,
                            interactive=False
                        )
                        
                        image_output = gr.Image(
                            label="Your Card",
                            type="filepath",
                            elem_classes="card-preview",
                            buttons=["download"]
                        )
                        
                        share_link_output = gr.Textbox(
                            label="Shareable Link",
                            info="Share this link with anyone to view the card",
                            interactive=False
                        )
                        
                        gr.Markdown(
                            """
                            ### 📥 How to Share
                            1. **Download**: Click the download button above the card
                            2. **Share Link**: Copy the shareable link to send to anyone
                            3. **High Resolution**: Cards are generated in 4K quality
                            """
                        )
                
                # Update description when template changes
                def update_template_desc(template_name):
                    return CARD_TEMPLATES[template_name]["description"]
                
                template_dropdown.change(
                    fn=update_template_desc,
                    inputs=[template_dropdown],
                    outputs=[template_description]
                )
                
                # Generate card button
                generate_btn.click(
                    fn=generate_greeting_card,
                    inputs=[
                        template_dropdown,
                        recipient_input,
                        message_input,
                        date_input,
                        details_input
                    ],
                    outputs=[image_output, share_link_output, status_output]
                )
            
            # ===== VIEW TAB =====
            with gr.Tab("🔗 View Shared Card"):
                gr.Markdown(
                    """
                    ### View a Shared Card
                    Enter a card ID to view a previously created card
                    """
                )
                
                with gr.Row():
                    card_id_input = gr.Textbox(
                        label="Card ID",
                        placeholder="Enter the card ID",
                        scale=3
                    )
                    view_btn = gr.Button("View Card", scale=1)
                
                view_output = gr.Image(
                    label="Card",
                    type="filepath",
                    buttons=["download"]
                )
                
                view_info = gr.JSON(label="Card Information")
                
                def view_shared_card(card_id):
                    """View a card by ID"""
                    if not card_id:
                        return None, {"error": "Please enter a card ID"}
                    
                    metadata = get_card_metadata(card_id)
                    if not metadata:
                        return None, {"error": "Card not found"}
                    
                    # Download image if available
                    if metadata.get("image_url"):
                        try:
                            import requests
                            response = requests.get(metadata["image_url"])
                            temp_path = f"/tmp/view_{card_id}.jpg"
                            with open(temp_path, "wb") as f:
                                f.write(response.content)
                            return temp_path, metadata
                        except:
                            return None, metadata
                    
                    return None, metadata
                
                view_btn.click(
                    fn=view_shared_card,
                    inputs=[card_id_input],
                    outputs=[view_output, view_info]
                )
            
            # ===== INFO TAB =====
            with gr.Tab("ℹ️ About"):
                gr.Markdown(
                    """
                    ## About AlexAI Greeting Cards
                    
                    Create stunning, personalized greeting cards for any occasion using AI-powered image generation.
                    
                    ### Features
                    - 🎨 **10 Beautiful Templates**: Birthday, Christmas, Halloween, Easter, Valentine's Day, Thanksgiving, New Year, Graduation, Wedding, and Thank You
                    - 🤖 **AI-Powered**: Uses Seedream-4.5 for high-quality 4K image generation
                    - 💎 **Professional Watermark**: Every card includes an elegant "AlexAI Cards" watermark
                    - ☁️ **Cloud Storage**: Cards are stored on Cloudflare R2 for reliable access
                    - 🔗 **Easy Sharing**: Generate shareable links to send your cards to anyone
                    - 📥 **High-Res Download**: Download cards in full 4K resolution
                    
                    ### How It Works
                    1. **Choose a Template**: Select from 10 occasion-specific templates
                    2. **Personalize**: Add recipient name, message, date, and custom details
                    3. **Generate**: AI creates a unique, high-quality card in seconds
                    4. **Share**: Download or share via link
                    
                    ### Technical Details
                    - **Image Model**: Seedream-4.5 by ByteDance
                    - **Resolution**: 4K (3840x2160)
                    - **Storage**: Cloudflare R2 Object Storage
                    - **Format**: JPEG with 95% quality
                    
                    ### Setup Requirements
                    To run this app, you need:
                    1. `REPLICATE_API_TOKEN` - Your Replicate API key
                    2. `R2_ACCOUNT_ID` - Cloudflare account ID
                    3. `R2_ACCESS_KEY_ID` - R2 access key
                    4. `R2_SECRET_ACCESS_KEY` - R2 secret key
                    5. `R2_BUCKET_NAME` - R2 bucket name
                    6. `R2_PUBLIC_URL` - Public URL for R2 bucket (optional)
                    
                    Created with ❤️ by AlexAI
                    """
                )
        
        return demo

# ===========================
# LAUNCH
# ===========================

if __name__ == "__main__":
    demo = create_card_interface()
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7860
    )