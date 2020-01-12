# Scripts

## find_code.py
**Download**: [`find_code.py`](./files/find_code.py)  
**Usage**: generate access codes for the [Frosty Keypad](./hints/h6.md) terminal hint.

```python
#!/usr/bin/env python3
"""2019 SANS Holiday Hack Challenge - Frosty Keypad."""
import itertools


def is_prime(number):
    """Verify if a number is a prime."""
    return 2 in [number, 2**number % number]


def main():
    """Execute."""
    digit_sets = [
        ['1', '1', '3', '7'],
        ['1', '3', '3', '7'],
        ['1', '3', '7', '7']
    ]

    primes = []

    for digits in digit_sets:
        for subset in itertools.permutations(digits):
            val = int(''.join(subset))
            if is_prime(val) and val not in primes:
                primes.append(val)
                print(f'{val} is a prime number')


if __name__ == "__main__":
    main()
```

## capteha_api.py
**Download**: [`capteha_api.py`](./files/capteha_api.py)   
**Usage**: bypass the CAPTHEHA in the [Bypassing the Frido Sleigh CAPTEHA](./objectives/o8.md) objective.

```python
#!/usr/bin/env python3
"""2019 SANS Holiday Hack Challenge - Bypassing the Frido Sleigh CAPTEHA."""
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

## token_proxy.py
**Download**: [`token_proxy.py`](./files/token_proxy.py)  
**Usage**: translate CSRF tokens for the [Retrieve Scraps of Paper from Server](./objectives/o9.md) objective.

```python
#!/usr/bin/env python3
"""2019 SANS Holiday Hack Challenge - Retrieve Scraps of Paper from Server."""
import requests
from flask import Flask, Response
app = Flask(__name__)


@app.route("/")
def token():
    """Return a token."""
    url = 'https://studentportal.elfu.org/validator.php'
    token = requests.Session().get(url).text
    # Put the token in the body, input tag, and header.
    resp = Response(
        f'Token:{token}\n'
        '<form>\n'
        f'  <input type="hidden" id="token" name="token" value="{token}"/>\n'
        '</form>\n'
    )
    resp.headers['token'] = token
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0')
```

## decrypt_pdf.py
**Download**: [`decrypt_pdf.py`](./files/decrypt_pdf.py)  
**Usage**: decrypt the PDF in the [Recover Cleartext Document](./objectives/o10.md) objective.

```python
#!/usr/bin/env python3
"""2019 SANS Holiday Hack Challenge - Recover Cleartext Document."""
from Crypto.Cipher import DES

seed = 0


def rand():
    """Generate random value."""
    # 1. get seed value
    # 2. multiply seed by 214013
    # 3. add 2531011 (this is our new seed value)
    # 4. right shift seed by 16
    # 5. bitwise AND with 32767
    global seed
    seed = (214013 * seed + 2531011)
    val = seed >> 16
    return (val & 32767)


def generate_key(val):
    """Generate encryption key."""
    global seed
    seed = val
    encrypted = []
    for _x in range(8):
        tmp = hex(rand())
        if len(str(tmp)) == 6:
            encrypted.append(str(tmp)[4:])
        elif len(str(tmp)) == 5:
            encrypted.append(str(tmp)[3:])
        elif len(str(tmp)) == 4:
            encrypted.append(str(tmp)[2:])
        elif len(str(tmp)) == 3:
            encrypted.append(f"0{str(tmp)[-1]}")
    return ''.join(encrypted)


def main():
    """Execute."""
    # File names
    encinfile = 'ElfUResearchLabsSuperSledOMaticQuickStartGuideV1.2.pdf.enc'
    pdfoutfile = 'ElfUResearchLabsSuperSledOMaticQuickStartGuideV1.2.pdf'

    # Friday, December 6, 2019 7:00:00 PM
    start = 1575658800

    # Loop over 2 hours and generate the key for each
    for x in range(7200):
        keyseed = start + x
        key = generate_key(keyseed)
        bytekey = bytearray.fromhex(key)

        # Prep for decrypting DES-CBC
        cipher = DES.new(
            bytekey,
            DES.MODE_CBC,
            iv=bytearray.fromhex('0000000000000000')
        )

        # Read encrypted file
        f = open(encinfile, 'rb')
        encrypted = f.read()

        # Decrypt using the current key
        msg = (cipher.iv + cipher.decrypt(encrypted))

        # Check if decryption was successful
        if msg[9:12] == b'PDF':
            # Yes, we got a PDF!
            print(f'Pass {x}: {key} decrypts to a PDF!')
            f = open(pdfoutfile, 'wb')
            f.write(msg)
            break
        else:
            # Womp womp! On to the next.
            print(f'Pass {x}: {key} is no bueno!')


if __name__ == "__main__":
    main()
```

## match_user_agents.py
**Download**: [`match_user_agents.py`](./files/match_user_agents.py)  
**Usage**: find additional bad IPs in the [Filter Out Poisoned Data Sources](./objectives/o12.md) objective.

```python
#!/usr/bin/env python3
"""2019 SANS Holiday Hack Challenge - Filter Out Poisoned Data Sources."""


def main():
    """Execute."""
    file_bad = 'IPs_bad.csv'
    file_all = 'IPs_all.csv'
    list_bad = []
    list_all = []

    # Read the full data log
    with open(file_all) as fp:
        line = fp.readline()

        while line:
            list_all.append(line.split('\t'))
            line = fp.readline()

    # Read the bad IP data and match on user_agent but only
    # keep the results if less than 4 matches are found.
    with open(file_bad) as fp:
        line = fp.readline()

        while line:
            tmp = []
            line_bad = line.split('\t')

            for line_all in list_all:
                if line_all[4] == line_bad[4]:
                    tmp.append(line_all[0])

            # Only add if less than 4 matches
            if len(tmp) < 4:
                list_bad.extend(tmp)

            # Add the original IP as well
            list_bad.append(line_bad[0])
            line = fp.readline()

    # Remove duplicates
    list_bad = list(dict.fromkeys(list_bad))

    # Tadaaaaa!
    print(f'Bad IPs: {",".join(list_bad)}')


if __name__ == "__main__":
    main()
```