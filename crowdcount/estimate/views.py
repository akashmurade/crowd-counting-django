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
matplotlib.use('Agg')
from matplotlib import cm as c
import matplotlib.pyplot as plt

# Load both models at startup
MODELS = {
    'dense': load_model('estimate/models/modelA.h5', safe_mode=False, compile=False),
    'sparse': load_model('estimate/models/modelB.h5', safe_mode=False, compile=False)
}

def preprocess_image(img_path):
    """Image preprocessing for CSRNet with resizing"""
    im = Image.open(img_path).convert('RGB')
    
    # Calculate new dimensions while maintaining aspect ratio
    max_dimension = 1024
    width, height = im.size
    
    if width > height:
        new_width = max_dimension
        new_height = int(height * (max_dimension / width))
    else:
        new_height = max_dimension
        new_width = int(width * (max_dimension / height))
    
    # Resize the image
    im = im.resize((new_width, new_height), Image.BILINEAR)
    
    # Convert to numpy array and normalize
    im = np.array(im) / 255.0
    im[..., 0] = (im[..., 0] - 0.485) / 0.229  # R
    im[..., 1] = (im[..., 1] - 0.456) / 0.224  # G
    im[..., 2] = (im[..., 2] - 0.406) / 0.225  # B
    
    return np.expand_dims(im, axis=0)

def predict_view(request):
    if request.method == 'POST' and request.FILES['image']:
        try:
            model_type = request.POST.get('model_type', 'dense')
            model = MODELS.get(model_type, MODELS['dense'])
            
            # Save uploaded file
            fs = FileSystemStorage()
            uploaded = request.FILES['image']
            filename = fs.save(uploaded.name, uploaded)
            input_path = fs.path(filename)
            
            # Process image
            img_array = preprocess_image(input_path)
            density_map = model.predict(img_array)
            count = np.sum(density_map)
            
            # Generate heatmap
            fig = plt.figure(figsize=(8, 8))
            plt.imshow(density_map[0,...,0], cmap=c.jet)
            plt.axis('off')
            
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=100)
            plt.close(fig)
            
            heatmap_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            return render(request, 'estimate/index.html', {
                'original': fs.url(filename),
                'heatmap_base64': heatmap_base64,
                'count': f'{count:.0f}',
                'selected_model': model_type,
                'is_dense_model': model_type == 'dense' or not model_type,
                'is_sparse_model': model_type == 'sparse'
            })

            
        except Exception as e:
            return render(request, 'estimate/index.html', {'error': str(e)})
    
    return render(request, 'estimate/index.html', {
        'is_dense_model': True,
        'is_sparse_model': False
    })
