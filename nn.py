"""
File with training functions.
"""


def train(data):
    """
    The function that sets the basic information for the training,
        initializes the conversion function,
        processes the data after training.
    :param data: (training info, filename, process id): (list, tuple):
    :return: None.
    """
    from wav import get_chunks_info, get_wav_info, compress_chunks, generate_wav
    from os import getcwd
    from LSTM import LSTM
    from datetime import datetime
    from uuid import uuid4
    from json import dump, dumps
    from requests import post
    filename = data[1]
    training_info = data[0]
    proc_id = str(data[2])

    training_info = {
        "chunks": int(training_info["chunks"]),
        "input": float(training_info["input"]),
        "lr": float(training_info["lr"]),
        "epochs": int(training_info["epochs"]),
        "batches": int(training_info["batches"])
    }

    chunks, info = get_wav_info(f"web/Upload/{filename}", split=training_info["chunks"])
    nets = [LSTM(training_info["lr"]) for i in range(len(chunks))]

    chunks_info = get_chunks_info(chunks)

    output_converter = lambda x: (x - chunks_info["min"]) / (
            chunks_info["max"] - chunks_info["min"])

    inp = [training_info["input"]]

    time = train_net(nets, chunks, output_converter, inp, training_info, proc_id)

    weights_id = uuid4()

    post(f"http://localhost:1000/sys/update-proc-info", data=dumps({"weights_id": str(weights_id),
                                                                    "proc_id": proc_id, "percent_done": 100,
                                                                    "text": {"msg_type": "finished",
                                                                             "style": "color: #d66024",
                                                                             "msg": str(time)
                                                                             }
                                                                    }))

    with open(f"{getcwd()}/web/Weights/{weights_id}.json", "w+") as fl:
        dump([
            {name: list(net.weights[name]) for name in net.weights}
            for net in nets
        ], fl)

    new_chunks = (net.calculate([inp] * len(chunk)) for chunk, net in zip(chunks, nets))
    new_chunks = compress_chunks(new_chunks)

    file = str(datetime.now()).replace(":", "_") + ".wav"

    print("File saved as:", file)
    generate_wav(file, info, new_chunks, chunks_info)

    post(f"http://localhost:1000/sys/update-proc-info", data=dumps({"percent_done": 100,
                                                                    "proc_id": proc_id,
                                                                    "text": {"msg_type": "audio ready",
                                                                             "style": "font-size: 4.4vw;",
                                                                             "msg": file
                                                                             }
                                                                    }))


def train_net(nets, chunks, output_converter, inp, training_info, proc_id):
    """
    Train Neural Network.
    :param nets: (tuple, list)
    :param chunks: numpy.ndarray;
    :param output_converter: lambda;
    :param inp: input for neural network: float;
    :param training_info: dict;
    :param proc_id: str;
    :return: time: datetime.timedelta.
    """
    from threading import Thread
    from requests import Session
    from json import dumps
    from datetime import datetime
    t = datetime.now()
    requests_session = Session()
    for index, net in enumerate(nets):
        if index % 500 == 0:
            print(index)
            session = {"percent_done": round(index / len(chunks) * 100, 2), "proc_id": proc_id,
                       "text": {"msg_type": "net_num", "style": "", "msg": str(index)}}

            t2 = Thread(target=requests_session.post,
                        kwargs={"url": f"http://localhost:1000/sys/update-proc-info", "data": dumps(
                            session)}, daemon=True)
            t2.start()

        inputs = inp * len(chunks[index])
        outputs = [output_converter(ampl) for ampl in chunks[index]]
        net.train(training_info["epochs"], training_info["batches"], (inputs, outputs))

    t1 = datetime.now()

    return t1 - t
