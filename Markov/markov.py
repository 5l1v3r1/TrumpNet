# -*- coding: utf-8 -*-
import random
import time

training_file = "belling_the_cat.txt"  ## Hahah what? :P

def read_data(filename):
    try:
        with open(filename) as tf:
            lines = tf.readlines()
        content = [x.strip() for x in lines]
        content = [content[i].split() for i in range(len(content))]
        content_list = content[0]
        return content_list
    except IOError:
        print("Error reading file, check filename or path.")

# The Markov chain itself
class Chain:

    '''
    # How this chain works
    This Markov chain implementation is rather simple really.
    The idea is that each node has associated with it a list of all known next states.
    We convert this list to a set of probabilities when we actually query the chain.
    This means that the internal representation:
        {'a': ['e', 'a', 'a', 'e', 'a'],
         'e': ['a', 'a', 'e', 'a', 'e', 'a', 'a', 'a', 'e', 'a']
        }
    Becomes:
        {'a': {'a': 0.6,
               'e': 0.4
              },
         'e': {'a': 0.7,
               'e': 0.3
              }
        }

    # A word on efficiency
    To manage this effectively, we keep both representations in each node.
    Large training sets would make this computation expensive to do every time.
    Because of this, we actually keep the two representations out of sync sometimes!
    The chain knows when it's recieving training data and when it's not via a `primed` boolean,
      indicating whether it's ready to recieve more training data.
    When we want to prime the chain so we can query it, we tell it to "prime" itself via the `prime()` method.
    Every time it primes itself, it'll recalculate the probabilities, and when it's accepting more training data
      it'll lose its primed-ness, allowing itself to fall safely out of sync
      (because we know we'll recalculate when we're done training the chain)
    *Note that we'll do this automatically if you use the chain's training mechanisms.*

    # How to use the chain
    If you have lots of training data and want to be efficient, run `chain.begin_training` to take the gloves off.
    Feed it pairs of training data with the `remember(initial_state, future_state)` method.
    If you're training the beginning of a sentence, make the initial state `mychain.beginning`.
    If you're training the end of a sentence, make the future state `mychain.end`
    When you're done with a large training set, run `chain.prime` to calibrate probabilities and "prime" all of the
      chain's nodes automatically.
    '''

    def __init__(self):

        # The list of all of the times a state transitions to another state, the first representation above
        self.__instance_chain = {}
        # Our sometimes-out-of-sync representation involving probabilities, the second representation above
        self.chain = {}

        # Add classes for the beginning and the end of speech
        class Beginning: pass
        class End: pass
        # Add instances of those classes so they're accessible for training data
        self.beginning = Beginning()
        self.end = End()

        self.primed = True # We're not being trained *right now*

        self.current_state = self.beginning

    def prime(self):
        self.chain = {}
        for node in self.__instance_chain:
            self.chain[node] = {}
            states_remembered = len(self.__instance_chain[node]) ## the number of future states we've visited (including duplicates) from this current node
            for future_state in self.__instance_chain[node]:
                if future_state not in self.chain[node].keys():
                    state_occurance_count = self.__instance_chain[node].count(future_state)
                    probability = state_occurance_count / float(states_remembered)
                    self.chain[node][future_state] = probability

        # Now we're back in sync, so we can say that we're primed again!
        self.primed = True

    def begin_training(self):
        # We'll just stay non-primed for a while, and won't re-calculate probabilities every time we're told something new.
        self.primed = False

    def remember(self, initial_state, future_state):
        ## If we're taking in information while we're also being used, recalculate probabilties immediately.
        ## This means that if we're currently primed, we'll leave this method also primed.
        recalculate_probabilities_immediately = self.primed

        ## Now, technically we're not currently primed.
        ## We know the two representations of the chain will be out of sync, and so we have to record that we're no longer in a primed state.
        self.primed = False

        ## Record the new information.
        if initial_state not in self.__instance_chain.keys():
            self.__instance_chain[initial_state] = []

        self.__instance_chain[initial_state].append(future_state)

        ## If we entered the method primed, also leave primed.
        if recalculate_probabilities_immediately:
            self.prime()

    # This Markov chain is actually also an iterator, allowing us to use the nice `for state in mychain:` syntax.
    # That means we need an __iter__ and a next()!
    # TODO: See about getting the same thing out of a generator instead of these magic methods.
    def __iter__(self):
        return self

    def next(self):
        choice = random.random()
        probability_reached = 0

        # Occasionally, we'll reach a symbol with nothing that leads on from it.
        # In that case, we've reached an implicit end, so jump to the end of the chain.
        if len(self.chain[self.current_state]) == 0:
            self.current_state = self.end

        for state, probability in self.chain[self.current_state].items():
            probability_reached += probability
            if probability_reached > choice:
                self.current_state = state

        # If we're at the end of the chain, don't keep iterating.
        if self.current_state == self.end:
            raise StopIteration

        # We're not at the end of the chain if we get here! So return whatever we've got.
        return self.current_state


    ## Lets us begin the chain traversal again.
    def reset(self):
        self.current_state = self.beginning

    def remember_sequence(self, sequence):
        self.begin_training()

        ## Add the beginning and end symbols to this sequence
        sequence.insert(0, self.beginning)
        sequence.insert(len(sequence), self.end)

        # Remember each pair in the sequence!
        for pos in range(len(sequence)-1):
            self.remember(sequence[pos], sequence[pos+1])

        self.prime()

    def generate_sequence(self, max_length="iterate forever"):
        sequence = []

        for element in chain:
            sequence.append(element)

            if len(sequence) == max_length:
                break

        return sequence


## So this runs only if we're not importing the chain and running it directly instead
if __name__ == "__main__":
    training_data = read_data(training_file)
    chain = Chain()
    chain.remember_sequence(training_data)
    print chain.generate_sequence(max_length=100)
