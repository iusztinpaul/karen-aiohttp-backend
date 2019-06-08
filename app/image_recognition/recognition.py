from imageai.Detection import ObjectDetection
import os
import base64
import time
# import aimanager

# Constants
dataset_string = 'dataset'
resnet_50_layer_model = 'resnet50_coco_best_v2.0.1.h5'
execution_path = f'{os.getcwd()}/app/image_recognition'
photos_path = f'{os.getcwd()}/app/photos'

output_path = f'{os.getcwd()}/app/output_photos'


class AIManager:

    def __init__(self):
        self.detector = ObjectDetection()
        self._init_detector_()
        self.custom_objects = self._init_custom_objects_()

    def _init_detector_(self):
        self.detector.setModelTypeAsRetinaNet()
        self.detector.setModelPath(os.path.join(execution_path, resnet_50_layer_model))
        self.detector.loadModel()

    def _init_custom_objects_(self):
        return self.detector.CustomObjects(cup=True, wine_glass=True, fork=True,
                                           knife=True, spoon=True, bowl=True,
                                           banana=True, apple=True, sandwich=True,
                                           person=True, orange=True, bottle=True)

    def process_image(self, input_image_folder):
        start = time.time()
        image = input_image_folder.split('/')[-1]
        # rest_path = input_image_folder.split('/')[:-1]

        inp_image_folder = os.path.join(photos_path, input_image_folder)
        detections = self.detector.detectCustomObjectsFromImage(
            custom_objects=self.custom_objects,
            input_image=inp_image_folder,
            output_image_path=f'{output_path}/{image}',
            input_type='file',
            output_type='file',
            minimum_percentage_probability=50
        )
        objects = []
        # Append the found objects
        for eachObject in detections:
            objects.append(eachObject)

        # If there are no objects found , delete the result photos
        if not objects:
            # os.remove(output_image_folder)
            os.remove(input_image_folder)
            end = time.time()
            print(end - start)
            return None, None

        # Convert image into base64
        with open(input_image_folder, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        end = time.time()
        print(end - start)

        return objects, encoded_string




# This method returns null if there is no results from a photo
def get_results_from_photos(dir, manager):
    names = os.listdir(dir)
    print(dir)
    for name in names:
        # photo_pull_full_path = os.path.join(dir, name)
        objects, base64obj = manager.process_image(name)
        yield objects, base64obj


def get_result_from_photo(photo, manager):
    objects, base64obj = manager.process_image(photo)
    return objects, base64obj