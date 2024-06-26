# from flask import Flask, render_template, request, url_for
# from werkzeug.utils import secure_filename
# import os
# import shutil
# from Task_3 import extract_features, find_closest_category, recommend_similar_images, compute_average_features, load_features_from_cache, save_features_to_cache, extract_features_from_category
# from tensorflow.keras.applications import EfficientNetB0

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'static/uploads'
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# model = EfficientNetB0(weights='imagenet', include_top=False, pooling='max')

# # Load features from cache if available
# category_features = load_features_from_cache()
# if category_features is None:
#     category_features = compute_average_features('dataset/test', model)
#     save_features_to_cache(category_features)

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file:
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             category, style = find_closest_category(file_path, category_features, model).split('_')
#             features = extract_features(file_path, model)
#             image_paths, features_list = extract_features_from_category('dataset/test', f"{category}_{style}", model)
#             recommended_images, similarity_scores = recommend_similar_images(features, features_list, image_paths)

#             recommended_image_paths = []
#             for img_path in recommended_images:
#                 dest_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(img_path))
#                 shutil.copy(img_path, dest_path)
#                 recommended_image_paths.append(os.path.basename(dest_path))

#             uploaded_image_url = os.path.basename(file_path)
#             recommendations = list(zip(recommended_image_paths, similarity_scores))
#             return render_template('index.html', uploaded_image=uploaded_image_url, recommendations=recommendations, category=category, style=style)
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)






# task 2============================================================================================
from flask import Flask, render_template, request, url_for # type: ignore
from werkzeug.utils import secure_filename # type: ignore
import os
import shutil
from Task_2 import extract_features, extract_features_from_dataset, recommend_similar_images
from tensorflow.keras.applications import EfficientNetB0 # type: ignore

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

model = EfficientNetB0(weights='imagenet', include_top=False, pooling='max')
image_paths, features_list = extract_features_from_dataset('dataset/test', model)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            features = extract_features(file_path, model)
            recommended_images, similarity_scores = recommend_similar_images(features, features_list, image_paths)

            recommended_image_paths = []
            for img_path in recommended_images:
                dest_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(img_path))
                shutil.copy(img_path, dest_path)
                recommended_image_paths.append(os.path.basename(dest_path))

            uploaded_image_url = os.path.basename(file_path)
            recommendations = list(zip(recommended_image_paths, similarity_scores))
            return render_template('index.html', uploaded_image=uploaded_image_url, recommendations=recommendations)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)