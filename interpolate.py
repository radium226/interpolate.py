#!/bin/env python

from collections import deque as Deque
import itertools
    
# https://github.com/tyarkoni/transitions

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def weird_range(min, max):
    for index, element in enumerate(range(min, max +1)):
        yield (index, None if (min + 5) < element and element < (max - 5) else element)
    
class Ring(object):

    def __init__(self, size):
        self.__deque = Deque(maxlen=size)
    
    def add(self, element):
        self.__deque.append(element)
    
    def last_added(self):
        return self.__deque[len(self.__deque) - 1]
    
    def clear(self):
        self.__deque.clear()
    
    def __iter__(self):
        yield from self.__deque

    def __len__(self):
        return len(self.__deque)

    def __getitem__(self, index):
        return self.__deque[index]

    def __repr__(self):
        return repr(self.__deque)
    
class Interpolate(object):

    def __init__(self, before_size, interpolatable_size, after_size):
        ring_size = before_size + interpolatable_size + after_size
        
        self.__before_size = before_size
        self.__interpolatable_size = interpolatable_size
        self.__after_size = after_size
        
        self.__ring = Ring(size=ring_size)
    
    def __partition_ring(self):
        def is_boundary(one_element, other_element):
            return one_element is None and other_element is not None or one_element is not None and other_element is None
        
        if len(self.__ring) == 1:
            return [[self.__ring[0]]]

        partitions = []
        partition = []
        first_pair = True
        for left_pair, right_pair in pairwise(filter(lambda pair: pair is not None, self.__ring)):
            left_index, left_element = left_pair
            right_index, right_element = right_pair
            
            # Deal with first partition
            if first_pair:
                partition.append(left_pair)
                first_pair = False
            
            if is_boundary(left_element, right_element):
                partitions.append(partition)
                partition = []
            
            partition.append(right_pair)
        
        # Deal with last partition
        if partition:
            partitions.append(partition)
        
        return partitions
    
    def __interpolate(self, pairs):
        def linear_interpolator(a, b):
            x_a, y_a = a
            x_b, y_b = b
            def f(x):
                return (x_b - x) / (x_b - x_a) * y_a + (x - x_a) / (x_b - x_a) * y_b
            return f
        a = pairs[self.__before_size - 1]
        b = pairs[len(pairs) - (self.__after_size - 1) - 1]
        f = linear_interpolator(a, b)
        
        return [a] + [(x, f(x)) for x in map(lambda pair: pair[0], pairs[self.__before_size:len(pairs) - (self.__after_size - 1) - 1])] + [b]
    
    def __iterate(self):
        
        def all_none(partition):
            return all(map(lambda pair: pair[1] is None, partition))
            
        def all_not_none(partition):
            return all(map(lambda pair: pair[1] is not None, partition))
        
        partitions = self.__partition_ring()
        
        # We should do something because it seems that we can interpolate, dude! 
        if len(partitions) == 3:
            assert len(partitions[0]) >= self.__before_size
            assert len(partitions[1]) <= self.__interpolatable_size
            assert len(partitions[2]) == self.__after_size
            
            interpolated = self.__interpolate([pair for partition in partitions for pair in partition])
            for pair in interpolated[self.__before_size:len(interpolated)]:
                yield pair
            self.__ring.clear()
        elif len(partitions) == 2:
            if all_not_none(partitions[0]) and all_none(partitions[1]):
                if len(partitions[1]) > self.__interpolatable_size: 
                    # We give up :(
                    yield from partitions[1]
                    self.__ring.clear()
                else:
                    pass # Continue, dude! 
            elif all_none(partitions[0]) and all_not_none(partitions[1]):
                yield from partitions[0]
                self.__ring.clear()
                for pair in partitions[1]:
                    self.__ring.add(pair)
            else:
                raise ValueError()# We should not be here... I guess. 
        elif len(partitions) == 1:
            if all_none(partitions[0]): # We're fucked anyway.
                yield from partitions[0]
                self.__ring.clear()
            else:
                index, element = self.__ring.last_added()
                if element is not None:
                    yield index, element
    
    def __call__(self, enumeration):
        for index, value in enumeration:
            self.__ring.add((index, value))
            yield from self.__iterate()
        
        partitions = self.__partition_ring()
        if len(partitions) > 0 and all(map(lambda pair: pair[1] is None, partitions[-1])):
            yield from partitions[-1]

if __name__ == "__main__":
    interpolate = Interpolate(before_size=1, interpolatable_size=3, after_size=1)
    for index, value in interpolate(weird_range(50, 70)):
        print("%(index)i = %(value)s" % {"index": index, "value": str(value) if value is not None else "None"})
