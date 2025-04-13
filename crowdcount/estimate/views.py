import os
import numpy as np
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from keras.saving import load_model
from PIL import Image
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from matplotlib import cm as c
import matplotlib.pyplot as plt

# Load model once at startup
MODEL = load_model('estimate/models/modelA.h5', safe_mode=False, compile=False)

def preprocess_image(img_path):
    """Image preprocessing for CSRNet"""
    im = Image.open(img_path).convert('RGB')
    im = np.array(im) / 255.0
    im[..., 0] = (im[..., 0] - 0.485) / 0.229  # R
    im[..., 1] = (im[..., 1] - 0.456) / 0.224  # G
    im[..., 2] = (im[..., 2] - 0.406) / 0.225  # B
    return np.expand_dims(im, axis=0)

def predict_view(request):
    if request.method == 'POST' and request.FILES['image']:
        try:
            # Save uploaded file
            fs = FileSystemStorage()
            uploaded = request.FILES['image']
            filename = fs.save(uploaded.name, uploaded)
            input_path = fs.path(filename)
            
            # Process image
            img_array = preprocess_image(input_path)
            density_map = MODEL.predict(img_array)
            count = np.sum(density_map)
            
            # Generate clean heatmap visualization
            fig = plt.figure(figsize=(8, 8))
            plt.imshow(density_map[0,...,0], cmap=c.jet)
            plt.axis('off')
            
            # Save to bytes buffer
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=100)
            plt.close(fig)
            
            # Convert to base64
            heatmap_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            return render(request, 'estimate/index.html', {
                'original': fs.url(filename),
                'heatmap_base64': heatmap_base64,
                'count': f'{count:.0f}'
            })
            
        except Exception as e:
            return render(request, 'estimate/index.html', {'error': str(e)})
    
    return render(request, 'estimate/index.html')