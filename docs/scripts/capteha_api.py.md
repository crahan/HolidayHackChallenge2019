# capteha_api.py
**Purpose**: bypass the CAPTHEHA in the [Bypassing the Frido Sleigh CAPTEHA](../challenges/c8.md) challenge.

```python
#!/usr/bin/env python3
# Image Recognition Using Tensorflow Exmaple.
# Code based on example at:
# https://raw.githubusercontent.com/tensorflow/tensorflow/master/tensorflow/examples/label_image/label_image.py
import os
import base64
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf  # noqa
tf.logging.set_verbosity(tf.logging.ERROR)
import numpy as np  # noqa
import threading  # noqa
import queue  # noqa
import time  # noqa
import requests  # noqa
import sys  # noqa
import json  # noqa

# sudo apt install python3-pip
# sudo python3 -m pip install --upgrade pip
# sudo python3 -m pip install --upgrade setuptools
# sudo python3 -m pip install --upgrade tensorflow==1.15


def load_labels(label_file):
    """Load labels."""
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label


def predict_image(
        q,
        sess,
        graph,
        image_bytes,
        img_uuid,
        labels,
        input_operation,
        output_operation):
    """Predict image."""
    image = read_tensor_from_image_bytes(image_bytes)
    results = sess.run(output_operation.outputs[0], {
        input_operation.outputs[0]: image
    })
    results = np.squeeze(results)
    prediction = results.argsort()[-5:][::-1][0]
    q.put({
        'img_uuid': img_uuid,
        'prediction': labels[prediction].title(),
        'percent': results[prediction]
    })


def load_graph(model_file):
    """Load graph."""
    graph = tf.Graph()
    graph_def = tf.GraphDef()
    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)
    return graph


def read_tensor_from_image_bytes(
        imagebytes,
        input_height=128,
        input_width=128,
        input_mean=0,
        input_std=255):
    """Read Tensor from image bytes."""
    image_reader = tf.image.decode_png(
        imagebytes,
        channels=3,
        name="png_reader"
    )
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(
        dims_expander,
        [input_height, input_width]
    )
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.compat.v1.Session()
    result = sess.run(normalized)
    return result


def main():
    """Execute."""
    # Loading the Trained Machine Learning Model created from
    # running retrain.py on the training_images directory
    graph = load_graph('./tmp/retrain_tmp/output_graph.pb')
    labels = load_labels("./tmp/retrain_tmp/output_labels.txt")

    # Load up our session
    input_operation = graph.get_operation_by_name("import/Placeholder")
    output_operation = graph.get_operation_by_name("import/final_result")
    sess = tf.compat.v1.Session(graph=graph)

    url = "https://fridosleigh.com/"

    # Create session
    s = requests.Session()

    # Get CAPTEHA images and types
    r = s.post(f'{url}api/capteha/request')
    if (r.json()['request']):
        images = r.json()['images']
        types = [x.strip() for x in r.json()['select_type'].split(',')]
        types[-1] = types[-1].replace('and ', '')

    # Can use queues and threading to spead up the processing
    q = queue.Queue()

    # Going to iterate over each of our images.
    for image in images:
        img_uuid = image['uuid']
        img_base64 = image['base64']
        print('Processing Image {}'.format(img_uuid))

        # We don't want to process too many images at once. 10 threads max
        while len(threading.enumerate()) > 10:
            time.sleep(0.0001)

        # Predict_image function is expecting png image bytes so we read
        # image as 'rb' to get a bytes object
        image_bytes = base64.b64decode(img_base64)
        threading.Thread(
            target=predict_image,
            args=(
                q,
                sess,
                graph,
                image_bytes,
                img_uuid,
                labels,
                input_operation,
                output_operation
            )
        ).start()

    print('Waiting For Threads to Finish...')
    while q.qsize() < len(images):
        time.sleep(0.001)

    # Getting a list of all threads returned results
    prediction_results = [q.get() for x in range(q.qsize())]
    answers = []

    # What are we looking for?
    print(f'Looking for {types}')

    # Get the matching images
    for prediction in prediction_results:
        if prediction['prediction'] in types:
            print(f"{prediction['img_uuid']} is a {prediction['prediction']}.")
            answers.append(prediction['img_uuid'])

    final_answer = ','.join(answers)

    # Submit CAPTHEHA answers
    json_resp = json.loads(
        s.post(
            f'{url}api/capteha/submit',
            data={'answer': final_answer}
        ).text
    )

    # WOMP WOMP
    if not json_resp['request']:
        # If it fails just run again. ML might get one wrong occasionally
        print('FAILED MACHINE LEARNING GUESS')
        print('-------\nOur ML Guess:\n--------\n{}'.format(final_answer))
        print('------\nServer Response:\n------\n{}'.format(json_resp['data']))
        sys.exit(1)

    # Found the CAPTEHA
    print('CAPTEHA Solved!')

    # If we get to here, we are successful and can submit a bunch
    # of entries till we win
    userinfo = {
        'name': 'Krampus Hollyfeld',
        'email': 'crahan@example.com',
        'age': 180,
        'about': "Cause they're so flippin yummy!",
        'favorites': 'thickmints'
    }
    # If we win the once-per minute drawing, it will tell us we were emailed.
    # Should be no more than 200 times before we win. If more, somethings
    # wrong.
    entry_response = ''
    entry_count = 1
    while 'crahan@example.com' not in entry_response and entry_count < 200:
        print(
            f'Submitting lots of entries until '
            f'we win the contest! Entry #{entry_count}'
        )
        entry_response = s.post(
            f'{url}api/entry',
            data=userinfo
        ).text
        entry_count += 1

    print(entry_response)


if __name__ == "__main__":
    main()
```
