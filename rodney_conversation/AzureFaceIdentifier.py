import io
import threading
import time
import uuid

import cv2
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials


class AzureFaceIdentifier:
    def __init__(self, endpoint, api_key, person_group_id):
        self.face_client = FaceClient(endpoint, CognitiveServicesCredentials(api_key))
        self.person_group_id = person_group_id
        self.known_persons = {}  # A cache for mapping person_id to UUID
        self.detected_uuids_queue = []  # Shared queue to hold detected UUIDs

        self.pause_event = threading.Event()
        self.pause_event.set()  # Start in the "run" state

    def identify_and_train_from_video(self):
        cap = cv2.VideoCapture(0)
        all_detected_uuids = set()
        try:
            while True:
                self.pause_event.wait()  # This will block if the event is cleared

                ret, frame = cap.read()
                if not ret:
                    break

                success, encoded_image = cv2.imencode('.jpg', frame)
                if not success:
                    continue

                # Detect the face in the frame
                detected_faces = self.face_client.face.detect_with_stream(io.BytesIO(encoded_image.tobytes()))

                face_ids = [face.face_id for face in detected_faces]

                # Identify the faces
                results = self.face_client.face.identify(face_ids, self.person_group_id)

                for face, person in zip(detected_faces, results):
                    # Draw bounding box
                    rect = face.face_rectangle
                    top, left, bottom, right = rect.top, rect.left, rect.top + rect.height, rect.left + rect.width
                    color = (0, 255, 0)  # Green

                    if len(person.candidates) > 0:
                        # Face is recognized
                        person_id = person.candidates[0].person_id
                        if person_id not in self.known_persons:
                            # Cache the person_id to UUID mapping
                            self.known_persons[person_id] = str(uuid.uuid4())
                        person_uuid = self.known_persons[person_id]
                    else:
                        # New face, assign a UUID and train
                        person_uuid = str(uuid.uuid4())
                        person = self.face_client.person_group_person.create(self.person_group_id, name=person_uuid)
                        self.face_client.person_group_person.add_face_from_stream(self.person_group_id,
                                                                                  person.person_id,
                                                                                  io.BytesIO(encoded_image.tobytes()))
                        self.known_persons[person.person_id] = person_uuid
                        self.train_person_group()

                    all_detected_uuids.add(person_uuid)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.putText(frame, person_uuid, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                cv2.imshow('Video', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

        # Instead of returning the UUIDs, we'll add them to the shared queue
        self.detected_uuids_queue.extend(list(all_detected_uuids))

    def train_person_group(self):
        self.face_client.person_group.train(self.person_group_id)
        while True:
            training_status = self.face_client.person_group.get_training_status(self.person_group_id)
            if training_status.status not in ['running', 'notstarted']:
                break
            time.sleep(5)

    def start_identification(self):
        # Start the identify_and_train_from_video function in a separate thread
        thread = threading.Thread(target=self.identify_and_train_from_video)
        thread.start()

    def get_detected_uuids(self):
        # A function to fetch detected UUIDs from the main loop
        uuids = list(self.detected_uuids_queue)
        self.detected_uuids_queue.clear()  # Clear the queue after fetching
        return uuids

    def pause_identification(self):
        self.pause_event.clear()  # Pause the thread

    def resume_identification(self):
        self.pause_event.set()  # Resume the thread
