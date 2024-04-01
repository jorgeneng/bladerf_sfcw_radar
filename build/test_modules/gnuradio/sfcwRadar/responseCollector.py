#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy
from gnuradio import gr
import pmt

class responseCollector(gr.basic_block):
    """
    docstring for block responseCollector
    """
    def __init__(self, tagName, offset):
        gr.basic_block.__init__(self,
            name="responseCollector",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        self.tagName = tagName
        self.offset = offset
        self.collection_ab_offsets= []

    def forecast(self, noutput_items, ninputs):
        # ninputs is the number of input connections
        # setup size of input_items[i] for work call
        # the required number of input items is returned
        #   in a list where each element represents the
        #   number of required items for each input
        ninput_items_required = [noutput_items] * ninputs
        return ninput_items_required

    def general_work(self, input_items, output_items):
        ninput_items = min([len(items) for items in input_items])
        noutput_items = 0

        tagTuple = self.get_tags_in_window(0,0,len(input_items[0]))


        for tag in tagTuple:
            if(pmt.to_python(tag.key) == self.tagName):# & (pmt.to_bool(tag.value)==True):
                #print('received a tag')
                #print('tag.offset: '+str(tag.offset))
                #print('self.nitems_read: '+str(self.nitems_read(0)))
                #print('input_items len: ' +str(len(input_items)))
                self.collection_ab_offsets.append(tag.offset+self.offset)
        #print(self.collection_ab_offsets)
        collection_re_index = []
        for collection_ab_index in self.collection_ab_offsets:
            #print('collection_ab_index: '+str(collection_ab_index))
            #print('self.nitems_read: '+str(self.nitems_read(0)))
            #print('input_items len: ' +str(len(input_items[0])))
        
            if collection_ab_index <= self.nitems_read(0)+len(input_items[0]):
                collection_re_index.append(self.nitems_read(0)-collection_ab_index+len(input_items[0]))
                #collection_re_index = self.nitems_read(0)-collection_ab_index+len(input_items[0])
                #print('extract: '+str(input_items[0][collection_re_index]))
                #self.collection_ab_offsets.pop(0)
                #noutput_items = 1
                #output_items[0][0] = input_items[0][collection_re_index]
            else:
                break
        noutput_items = len(collection_re_index)
        output_items_index = 0
        for re_index in collection_re_index:
            #print('extract: '+str(input_items[0][re_index]))
            output_items[0][output_items_index] = input_items[0][re_index]
            output_items_index = output_items_index + 1
            self.collection_ab_offsets.pop(0)
        #noutput_items = len(relativeOffsetList)
        #for index in range(noutput_items):
            #inputIndex = relativeOffsetList[index]+self.offset
            #print(inputIndex)
            #print('extract: '+str(input_items[0][inputIndex]))
            #output_items[0][index] = input_items[0][inputIndex]
        # For this sample code, the general block is made to behave like a sync block
        #noutput_items = min(len(output_items[0]), ninput_items)
        #noutput_items = 1#min(len(output_items[0]), ninput_items)
        #output_items[0][0] = 1#input_items[0][ninput_items]
        #self.consume_each(noutput_items)
        self.consume(0,len(input_items[0]))
        #print(len(output_items))
        return noutput_items

