#!/usr/bin/env drgn
# SPDX-License-Identifier: GPL-3.0-or-later

"""Decode a read/write semaphore whose address has been passed as argument"""

import os
import sys
from drgn import Object
from drgn.helpers.linux.list import list_for_each_entry

RWSEM_WRITER_LOCKED = (1 << 0)
RWSEM_FLAG_WAITERS  = (1 << 1)
RWSEM_FLAG_HANDOFF  = (1 << 2)
#Bits 8-62(i.e. 55 bits of counter indicate number of current readers that hold the lock)
RWSEM_READER_MASK=0x7fffffffffffff00 #Bits 8-62 - 55-bit reader count

def get_waiters(rwsem):
	print("\n ##### rwsem.wait_list state #####\n")
	for waiter in list_for_each_entry(
		"struct rwsem_waiter", rwsem.wait_list.address_of_(), "list"):
		ts = Object(prog, "struct task_struct", address=waiter.task.value_())
		print(ts.comm.string_())
		pid = ts.pid.value_()
		trace = prog.stack_trace(pid)
		print(trace)
		print("************************")

def get_owner_info(rwsem):
	print("\n ##### rwsem.owner state #####\n")
	#If LSB of rwsem.count is set, rwsem is owned by a writer
	owner_is_writer = (rwsem.count.counter.value_() & 1)
	# To confirm that rwsem is owned by a reader, 3 conditions
	# should be true
	#  1. Reader count i.e bits 8-62 of rwsem.count should have some
	#     non-zero value
	#  2. LSB of rwsem.owner should be set
	#  3. LSB of rwsem.count should not be set 
	owner_is_reader = ((rwsem.count.counter.value_() & RWSEM_READER_MASK)
		& (rwsem.owner.counter.value_() & 1)
		& (owner_is_writer == 0))

	# A free rwsem will have rwsem.count as 0. It may or may not have
	# rwsem.owner as 0. If a writer takes a rwsem it puts task_struct
	# in the owner field and this gets cleared when writer releases the
	# rwsem. But if a reader takes a rwsem it puts task_struct | 
	# RWSEM_READER_OWNED in the owner field and the owner field not fully
	# cleared when reader releases the lock. So if a free rwsem has some
	# task_struct info in owner, that task_struct would be the last
	# reader owners of this rwsem
	free = rwsem.count.counter.value_()
	print("Owner information for rwsem %s is as follows." % str(hex(addr)))
	if owner_is_writer:
		print( "It is owned by a writer with task_struct %s ." % str(hex(rwsem.owner.counter.value_() & 0xffffffffffffffff)))
	elif owner_is_reader: 
		num_readers = rwsem.count.counter.value_() & RWSEM_READER_MASK;
		last_owner = (rwsem.owner.counter.value_() & 0xffffffffffffffff) - 1;
		print("It is owned by %d reader(s) and last acquirer is %x" % (num_readers, last_owner))
	elif free:
		print("It is currently free")
		if rwsem.owner.counter.value_():
			last_owner = (rwsem.owner.counter.value_() & 0xffffffffffffffff) - 1;
			print("But it was last owned by a reader task_struct:" + str(hex(last_owner)));

def get_counter_info(rwsem):
	val = rwsem.count.counter.value_()
	print("\n ##### rwsem.count state ##### \n")
	print("RWSEM_WRITER_LOCKED: ", (val & RWSEM_WRITER_LOCKED))	
	print("RWSEM_FLAG_WAITERS: ", (val & RWSEM_FLAG_WAITERS) >> 1)	
	print("RWSEM_FLAG_HANDOFF: ", (val & RWSEM_FLAG_HANDOFF) >> 2)	
	print("RWSEM_READER_COUNT: ", (val & RWSEM_READER_MASK) >> 8)	

addr = int(sys.argv[1], 16)


rwsem = Object(prog, 'struct rw_semaphore', address=addr)


get_owner_info(rwsem)
get_waiters(rwsem)
get_counter_info(rwsem)
