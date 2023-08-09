import json
from uuid import uuid4
from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import FaceAttributeType
from msrest.authentication import CognitiveServicesCredentials

class RecognizedPerson:
    @staticmethod
    def load_from_json(json_file, face_image):
        # TODO: implement
        # Face recognition info for a uuid is stored in ./rodney_ai/data/faces/<uuid_here_no_angled_brackets>.json
        pass

    def __init__(self, uuid=str(uuid4().hex)):
        self.uuid = uuid
        self.first_name = None
        self.last_name = None
        self.notes = ""


class FacialDetection:

    # Set up the FaceClient with your endpoint and key
    face_client = FaceClient('<YOUR_ENDPOINT>', CognitiveServicesCredentials('<YOUR_API_KEY>'))

    # Detect faces
    image_path = "path_to_your_image.jpg"
    with open(image_path, 'rb') as image:
        detected_faces = face_client.face.detect_with_stream(image)

    # If faces are detected, print their IDs
    if detected_faces:
        for face in detected_faces:
            print(face.face_id)
    else:
        print("No face detected!")


class RodneyConversation:
    def __init__(self):
        # Idea is to have facial recognition identify people
        self.people_in_conversation = []
        self.known_embeddings_path = r"C:\Users\tenant\PycharmProjects\rodney-v2\rodney_ai\data\known_face_embeddings.json"

