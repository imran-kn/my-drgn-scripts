#!/usr/bin/env drgn
# SPDX-License-Identifier: GPL-3.0-or-later

"""Decode a read/write semaphore whose address has been passed as argument"""

import os
import sys
from drgn import Object
from drgn.helpers.linux.list import list_for_each_entry

def print_waiters(rwsem):
	for waiter in list_for_each_entry(
		"struct rwsem_waiter", rwsem.wait_list.address_of_(), "list"):
		ts = Object(prog, "struct task_struct", address=waiter.task.value_())
		print(ts.comm.string_())
		pid = ts.pid.value_()
		trace = prog.stack_trace(pid)
		print(trace)
		print("************************")

def get_owner_info(rwsem):
	#If LSB of rwsem.count is set, rwsem is owned by a writer
	write_owner = (rwsem.count.counter.value_() & 1)
	# To confirm that rwsem is owned by a reader, 3 conditions
	# should be true
	#  1. Reader count i.e bits 8-62 of rwsem.count should have some
	#     non-zero value
	#  2. LSB of rwsem.owner should be set
	#  3. LSB of rwsem.count should not be set 
	read_owner = ((rwsem.count.counter.value_() & RWSEM_READER_MASK)
		& (rwsem.owner.counter.value_() & 1)
		& (write_owner == 0))

	# A free rwsem will have rwsem.count as 0. It may or may not have
	# rwsem.owner as 0. If a writer takes a rwsem it puts task_struct
	# in the owner field and this gets cleared when writer releases the
	# rwsem. But if a reader takes a rwsem it puts task_struct | 
	# RWSEM_READER_OWNED in the owner field and the owner field not fully
	# cleared when reader releases the lock. So if a free rwsem has some
	# task_struct info in owner, that task_struct would be the last
	# reader owners of this rwsem
	free = rwsem.count.counter.value_()
	if write_owner:
		print(str(hex(addr)) + " is owned by a writer.")
		print("Owner task_struct: " + str(hex(rwsem.owner.counter.value_() & 0xffffffffffffffff)))
	elif read_owner: 
		print(str(hex(addr)) + " is owned by a reader.")
	elif free:
		print(str(hex(addr)) + " is currently free")
		if rwsem.owner.counter.value_():
			last_owner = (rwsem.owner.counter.value_() & 0xffffffffffffffff) - 1;
			print("But it was last owned by a reader task_struct:" + str(hex(last_owner)));

addr = int(sys.argv[1], 16)

#Bits 8-62(i.e. 55 bits of counter indicate number of current readers that hold the lock)
RWSEM_READER_MASK=0x7fffffffffffff00 #Bits 8-62 - 55-bit reader count

rwsem = Object(prog, 'struct rw_semaphore', address=addr)


get_owner_info(rwsem)
get_waiters(rwsem)
