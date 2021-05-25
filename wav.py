"""
File for working with .wav
"""


def get_wav_info(fl, split=44100):
    """

    :param fl: file name: str;
    :param split: number of chunk splits: int;
    :return: chunks: numpy.ndarray & wav info: dict,
    """
    from scipy.io import wavfile
    from numpy import array_split

    samplerate, data = wavfile.read(fl)
    length, channels = data.shape[0], data.shape[1] if len(data.shape) == 2 else 1
    with open(fl, "rb") as fl:
        bytes_ = fl.read(44)

    info = {
        "ChunkID": bytes_[:4],
        "ChunkSize": int.from_bytes(bytes_[4:8], "little"),
        "Format": bytes_[8: 12],
        "SubChunk1ID": bytes_[12:16],
        "SubChunk1Size": int.from_bytes(bytes_[16:20], "little"),
        "AudioFormat": int.from_bytes(bytes_[20:22], "little"),
        "Channels": channels,
        "SampleRate": samplerate,
        "ByteRate": int.from_bytes(bytes_[28:32], "little"),
        "BlockAlign": int.from_bytes(bytes_[32:34], "little"),
        "BitsPerSample": int.from_bytes(bytes_[34:36], "little"),
        "Length": length,
    }

    data = array_split(data, split)
    if channels == 2:
        data = convert2mono(data)
    else:
        data = data

    chunks_info = get_chunks_info(data)
    div = int(f"1{max(0, len(str(int(chunks_info['max']))) - 5) * '0'}")

    return [value / div for value in data], info


def append_to_wav(fl, element, bytes_size=0, byteorder="", signed=False):
    """
    Appending bytes to file.
    :param fl: file: file;
    :param element: element to append: (str, int);
    :param bytes_size: bytes size: int;
    :param byteorder: bytes order (little / big): str;
    :param signed: Signed or Not int: bool.
    :return: None.
    """
    if isinstance(element, (int, float)):
        fl.write(int(element).to_bytes(bytes_size, byteorder=byteorder, signed=signed))
    elif isinstance(element, str):
        fl.write(bytes(element, "ascii"))


def generate_wav(name, info, chunks, chunks_info, _deconverter=True):
    """
    Generates .wav
    :param name: name: str;
    :param info: wav info: dict;
    :param chunks: chunks: numpy.ndarray;
    :param chunks_info: chunks info: dict;
    :param _deconverter: use deconverter: bool;
    :return: None.
    """
    with open("web/static/Generated/" + name, "a+b") as fl:
        append_to_wav(fl, "RIFF")
        append_to_wav(fl, "----")
        append_to_wav(fl, "WAVE")

        append_to_wav(fl, "fmt ")
        append_to_wav(fl, info["SubChunk1Size"], 4, "little", True)
        append_to_wav(fl, 1, 2, "little", True)
        append_to_wav(fl, 1, 2, "little", True)
        append_to_wav(fl, info["SampleRate"], 4, "little", True)
        append_to_wav(fl, info["SampleRate"] * info["BitsPerSample"] * info["Channels"] / 8, 4, "little", True)
        append_to_wav(fl, info["BitsPerSample"] * info["Channels"] / 8, 2, "little", True)
        append_to_wav(fl, info["BitsPerSample"], 2, "little", True)

        append_to_wav(fl, "data")
        append_to_wav(fl, "----")

        preAudioPosition = fl.tell()

        chunks_info = {"max": 30000, "min": -30000}

        if _deconverter:
            deconverter = lambda y: (chunks_info["max"] * y - chunks_info["min"] * y + chunks_info["min"])
        else:
            deconverter = lambda y: y

        for ampl in chunks:
            append_to_wav(fl, int(round(deconverter(abs(ampl)))), 2, "little", signed=True)
            print(ampl, deconverter(ampl))
        position = fl.tell()

    with open("web/static/Generated/" + name, "r+b") as fl:
        fl.seek(preAudioPosition - 4)
        append_to_wav(fl, position - preAudioPosition, 4, "little", True)
        fl.seek(4, 0)
        append_to_wav(fl, position - 8, 4, "little", True)


def compress_chunks(chunks):
    """
    Compress Chunks
    :param chunks: chunks: numpy.ndarray;
    :return: compressed chunks: numpy.ndarray;
    """
    from numpy import array
    return array([data["outputs_cell"] for chunk in chunks for data in chunk])


def get_chunks_info(chunks):
    """
    Get info about chunks (max and min values)
    :param chunks: chunks: numpy.ndarray;
    :return: dict;
    """
    from numpy import array
    if isinstance(chunks[0], (list, tuple, type(array([])))):
        maximum = max([max(chunk) for chunk in chunks])
        minimum = min([min(chunk) for chunk in chunks])

    else:
        maximum = max(chunks)
        minimum = min(chunks)

    return {"max": maximum, "min": minimum}


def convert2mono(chunks):
    """
    Converts stereo to mono
    :param chunks: chunks: numpy.ndarray;
    :return: mono chunks: numpy.ndarray;
    """
    from numpy import array
    return array([array([sum(data) / len(data) for data in chunk]) for chunk in chunks])
