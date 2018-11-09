import numpy
import scipy.special
# neural network class definition
class neuralNetwork :

    # initialise the neural network
    def __init__(self, inputnodes, hiddennodes, outputnodes, learningrate):
        self.inodes = inputnodes
        self.hnodes = hiddennodes
        self.onodes = outputnodes

        self.lr = learningrate

        #Generate Weight, -0.5 means 1/sqrt(in_nodes)
        #It depends on the nodes transfered in 
        #行数是输入节点的数量，列数是输出节点的数量
        self.w_ih = numpy.random.normal(0.0, pow(self.inodes, -0.5), (self.hnodes, self.inodes))
        self.w_ho = numpy.random.normal(0.0, pow(self.hnodes, -0.5), (self.onodes, self.hnodes))

        pass
    
    # train the neural network
    def train(self, inputs_list, targets_list):
        targets = numpy.array(targets_list,ndmin = 2).T
        inputs = numpy.array(inputs_list, ndmin = 2).T

        hidden_inputs = numpy.dot(self.w_ih, inputs)
        hidden_outputs = scipy.special.expit(hidden_inputs)
        final_inputs = numpy.dot(self.w_ho, hidden_outputs)
        final_outputs = scipy.special.expit(final_inputs)

        #计算输出节点的错误
        output_errors = targets - final_outputs
        #计算隐藏节点的错误，该错误通过权重相乘，因此权重需要转置
        hidden_errors = numpy.dot(self.w_ho.T, output_errors)

        #修正权重，方法见公式
        self.w_ho += self.lr * numpy.dot((output_errors * final_outputs * (1.0 - final_outputs)), numpy.transpose(hidden_outputs))
        self.w_ih += self.lr * numpy.dot((hidden_errors * hidden_outputs * (1.0 - hidden_outputs)), numpy.transpose(inputs))
        pass

    # query the neural network
    def query(self, inputs_list):
        #行向量转换为列向量
        inputs = numpy.array(inputs_list, ndmin = 2).T
        #用权重点乘输入，因此行数是输出节点数，列数是输入节点数
        hidden_inputs = numpy.dot(self.w_ih, inputs)
        #通过sigmoid函数，变成节点输出
        hidden_outputs = scipy.special.expit(hidden_inputs)
        final_inputs = numpy.dot(self.w_ho, hidden_outputs)
        final_outputs = scipy.special.expit(final_inputs)
        return final_outputs

inputNodes = 784
hiddenNodes = 100
outputNodes = 10
learningRate = 0.3
n = neuralNetwork(inputNodes,hiddenNodes,outputNodes,learningRate)

data_file = open("mnist_train.csv",'r')
data_list = data_file.readlines()
data_file.close()
for i in range(10000):
    all_values = data_list[i].split(',')
    scaled_input = (numpy.asfarray(all_values[1:])/255.0 * 0.99)+0.01
    targets = numpy.zeros(outputNodes) + 0.01
    targets[int(all_values[0])] = 0.99
    n.train(scaled_input, targets)
data_file = open("mnist_test.csv",'r')
data_list = data_file.readlines()
data_file.close()
for i in range(10):
    all_values = data_list[i].split(',')
    scaled_input = (numpy.asfarray(all_values[1:])/255.0 * 0.99)+0.01
    print(n.query(scaled_input))
    print(all_values[0])
