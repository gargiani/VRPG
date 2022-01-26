import torch
import torch.nn as nn

class GaussianPolicy:

    def __init__(self, neural_mean, variance):

        self.variance = variance
        self.neural_net = neural_mean
        self.policy = None
        
    def distribution(self, observation):
      
        self.policy = torch.distributions.multivariate_normal.MultivariateNormal(self.neural_net(observation), covariance_matrix=self.variance)

    def sample(self):

        if self.policy == None:
            raise ValueError("Distribution not defined!")
        else:
            return self.policy.sample()     

    def log_prob(self, observations, actions, batch_size):

        self.distribution(observations)
        
        return (1/batch_size)*self.policy.log_prob(actions) 
        
class Neural_SoftMax:

    def __init__(self, neural_net, action_space):

        self.action_space = torch.tensor(action_space, dtype=torch.float32)
        self.neural_net = neural_net
        self.softmax = nn.Softmax(dim=1)
        self.policy = None 

    def distribution(self, observations):

        features = self.neural_net(observations)
        self.policy = self.softmax(features)

    def sample(self):
        
        if self.policy == None:
            raise ValueError("Distribution not defined!")
        else:
            
            m = torch.distributions.Multinomial(1, self.policy)
            actions_idx = m.sample()
            actions = torch.zeros(actions_idx.shape[0], dtype=torch.int64)

            for ii, idx in enumerate(actions_idx):
                actions[ii] = (idx*self.action_space).sum()

            return actions

    def log_prob(self, observations, actions, batch_size):

        self.distribution(observations)
        actions_idx = torch.unsqueeze(actions, 1)
        
        return (1/batch_size)*torch.log(torch.gather(self.policy, 1, actions_idx))
        
        
class neuralnet(nn.Module):
    
    def __init__(self, input_size, output_size, hidden_layers, activation = nn.Tanh()):
        super(neuralnet, self).__init__()

        modules = []
        hidden_layers.insert(0, input_size)
        
        for ii, _ in enumerate(hidden_layers[:-1]):
            modules.append(nn.Linear(hidden_layers[ii], hidden_layers[ii+1]))
            modules.append(activation)
        
        modules.append(nn.Linear(hidden_layers[-1], output_size))

        self.sequential = nn.Sequential(*modules)

    def forward(self, x):    
        return self.sequential(x)
