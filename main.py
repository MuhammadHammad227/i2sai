from flask import Flask, request, render_template_string
import cv2
import numpy as np
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return '''
        <!doctype html>
        <title>Upload an Image</title>
        <h1>Upload an Image</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
          <input type="file" name="file">
          <input type="submit" value="Upload">
        </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    # Read the image file
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)
    in_memory_file.seek(0)
    
    # Convert the image to OpenCV format
    image = np.frombuffer(in_memory_file.read(), np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # Process the image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted_image = cv2.bitwise_not(gray_image)
    blur_image = cv2.GaussianBlur(inverted_image, (21, 21), 0)
    inverted_blur = cv2.bitwise_not(blur_image)
    sketch = cv2.divide(gray_image, inverted_blur, scale=256.0)

    # Convert the processed image to byte stream
    _, buffer = cv2.imencode('.png', sketch)
    byte_stream = io.BytesIO(buffer)
    
    # Encode image to Base64
    sketch_data_url = "data:image/png;base64," + base64.b64encode(byte_stream.getvalue()).decode()

    # Render HTML with the image
    return render_template_string('''
        <!doctype html>
        <title>Sketch Result</title>
        <h1>Your Sketch</h1>
        <img src="{{ sketch_url }}" alt="Sketch">
        <br>
        <a href="/">Upload another image</a>
    ''', sketch_url=sketch_data_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
