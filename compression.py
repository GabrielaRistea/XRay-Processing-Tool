import numpy as np
import pickle
import zlib


def compress_universal(image_matrix):
    img_bytes = image_matrix.tobytes()
    compressed_bytes = zlib.compress(img_bytes, level=9)
    return compressed_bytes


def save_compressed_file(compressed_bytes, original_shape, original_dtype, filename, patient_data=None):
    if patient_data is None:
        patient_data = {}

    archive_data = {
        'shape': original_shape,
        'dtype': original_dtype,
        'image_data': compressed_bytes,
        'patient_data': patient_data
    }

    with open(filename, 'wb') as f:
        pickle.dump(archive_data, f)

    return filename


def decompress_universal(file_obj):
    file_obj.seek(0)
    archive_data = pickle.load(file_obj)

    compressed_bytes = archive_data['image_data']
    img_bytes = zlib.decompress(compressed_bytes)

    reconstructed_img = np.frombuffer(img_bytes, dtype=archive_data['dtype'])
    reconstructed_img = reconstructed_img.reshape(archive_data['shape'])

    patient_data = archive_data.get('patient_data', {})

    return reconstructed_img, patient_data