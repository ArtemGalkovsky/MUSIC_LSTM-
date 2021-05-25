"""
File for LSTM class.
"""

import numpy as np


class LSTM:
    """
    LSTM Neural Network Class.
    """

    __slots__ = ["weights", "biases", "cells", "activation_functions", "lr"]

    def __init__(self, lr):
        """
        Initialize LSTM.
        :param lr: Learning Rate: float.
        """
        from numpy import zeros, random, tanh, exp

        self.lr = lr

        self.weights = {
            "Forget": random.random_sample(2),
            "Output": random.random_sample(2),
            "Input Sigm": random.random_sample(2),
            "Input Tanh": random.random_sample(2)
        }

        self.biases = {
            "Forget": 0,
            "Output": 0,
            "Input Sigm": 0,
            "Input Tanh": 0,
        }

        self.cells = {"memory": zeros(2), "outputs": zeros(2)}

        sigm = lambda x: 1 / (1 + exp(-x))
        self.activation_functions = {
            "sigm": sigm,
            "tanh": tanh,
            "dsigm": lambda x: sigm(x) * (1 - sigm(x)),
            "dtanh": lambda x: 1 - tanh(x) * tanh(x)
        }

    def __multiply(self, inp, t=0):
        """
        Calculates one output
        :param inp: input value: int;
        :return: output values: dict.
        """

        from numpy import append, column_stack

        w, b, c, act_funcs = self.weights, self.biases, self.cells, self.activation_functions

        last_input, last_memory = c["outputs"][t - 1], c["memory"][t - 1]
        inputs = column_stack((last_input, inp)).ravel()

        values = {}

        values["last_input"] = last_input
        values["last_memory"] = last_memory

        values["forget"] = act_funcs["sigm"](w["Forget"] @ inputs + b["Forget"])
        values["input_sigm"] = act_funcs["sigm"](w["Input Sigm"] @ inputs + b["Input Sigm"])
        values["input_tanh"] = act_funcs["tanh"](w["Input Tanh"] @ inputs + b["Input Tanh"])
        values["output"] = act_funcs["sigm"](w["Output"] @ inputs + b["Output"])

        values["memory_cell"] = last_memory * values["forget"] + values["input_sigm"] * values["input_tanh"]
        values["outputs_cell"] = values["output"] * act_funcs["tanh"](values["memory_cell"])

        c["memory"] = append(c["memory"], values["memory_cell"])
        c["outputs"] = append(c["outputs"], values["outputs_cell"])

        return values

    def calculate(self, inputs):
        """
        Calculate many;
        :param inputs: (list, tuple, array);
        :return: generator;
        """
        return (self.__multiply(inp) for inp in inputs)

    def calculate_gradients(self, values, true_output):
        """
        Calculate Gradients
        :param values: self.__multiply return;
        :param true_output: (array, int, float...);
        :return: gradients: dict, values: dict, loss: float.
        """
        act_funcs = self.activation_functions
        w = self.weights

        loss = -(true_output - values["outputs_cell"])

        output_gradient = act_funcs["dsigm"](values["output"]) \
                          * act_funcs["tanh"](values["outputs_cell"]) * loss

        memory_cell = values["output"] * loss * act_funcs["dtanh"](values["memory_cell"])

        forget_gradient = act_funcs["dsigm"](values["forget"]) * values["memory_cell"] * memory_cell

        input_sigm_gradient = act_funcs["dsigm"](values["input_sigm"]) * values["input_tanh"] * memory_cell

        input_tanh_gradient = act_funcs["dtanh"](values["input_sigm"]) * memory_cell

        # GATE WEIGHTS GRADIENTS

        last_input = values["last_input"].T

        forget_weights = last_input * forget_gradient
        # Bias: forget_gradient
        forget_input = forget_gradient * w["Forget"].T

        input_sigm_weights = last_input * input_sigm_gradient
        # Bias: input_sigm_gradient
        input_sigm_input = input_sigm_gradient * w["Input Sigm"].T

        output_weights = last_input * output_gradient
        # Bias: output_gradient
        output_input = output_gradient * w["Output"].T

        input_tanh_weights = last_input * input_tanh_gradient
        # Bias: input_tanh_gradient
        input_tanh_input = input_tanh_weights * w["Input Tanh"].T

        input_gradient = output_input + input_tanh_input + input_sigm_input + forget_input

        values["last_input"] = input_gradient
        values["last_memory"] = values["forget"] * memory_cell

        gradients = {
            "forget_weights": forget_weights,
            "input_sigm_weights": input_sigm_weights,
            "input_tanh_weights": input_tanh_weights,
            "output_weights": output_weights
        }

        return gradients, values, loss

    def walk_through_batch(self, chunks):
        """
        Go Trough Batch.
        :param chunks: chunks: numpy.ndarray;
        :return: gradients: dict.
        """
        from numpy import array

        values = (self.__multiply(value) for value in chunks[0])

        grads = array([array(list(self.calculate_gradients(value, output)[0].values())) for output, value in
                       reversed(tuple(zip(chunks[1], values)))])
        grads = np.sum(grads, axis=0)

        return {"forget_weights": grads[0], "input_sigm_weights": grads[1],
                "input_tanh_weights": grads[2], "output_weights": grads[3]}

    def train(self, epochs, batches, chunks):
        """
        Training LSTM.
        :param epochs: int;
        :param batches: int;
        :param chunks: numpy.ndarray;
        :return: None.
        """
        from numpy import array

        for epoch in range(epochs):
            for batch in range(batches):
                gradients = self.walk_through_batch(chunks)
                self.update_weights(gradients)
                self.cells = {"outputs": array([0.5, 0.5]), "memory": array([0., 0.])}

    def update_weights(self, gradients):
        """
        Updating Weights.
        :param gradients: dict;
        :return: None.
        """
        w, lr = self.weights, self.lr

        w["Forget"] = w["Forget"] - lr * gradients["forget_weights"]
        w["Output"] = w["Output"] - lr * gradients["output_weights"]
        w["Input Sigm"] = w["Input Sigm"] - lr * gradients["input_sigm_weights"]
        w["Input Tanh"] = w["Input Tanh"] - lr * gradients["input_tanh_weights"]
