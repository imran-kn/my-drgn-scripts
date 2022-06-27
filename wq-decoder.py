#!/usr/bin/env drgn
# SPDX-License-Identifier: GPL-3.0-or-later

"""Dump workqueue and worker_pool states"""

import os
import sys
from drgn import Object
from drgn.helpers.linux.idr import idr_for_each
from drgn.helpers.linux.list import *

def dump_worker_pool_states():
	for elem in idr_for_each(prog['worker_pool_idr'].address_of_()):
		worker_pool_address = elem[1].value_()
		worker_pool = Object(prog, 'struct worker_pool', address=worker_pool_address)
		print("worker_pool: ", hex(worker_pool_address),
		      " id: ", worker_pool.id.value_(),
		      " cpu: ", worker_pool.cpu.value_(),
		      " nr_idle ", worker_pool.nr_idle.value_(),
		      " nr_workers: ", worker_pool.nr_workers.value_(), "\n")

		if (list_empty(worker_pool.worklist.address_of_())):
			print("There are no pending work items on this pool \n")
		else:
			print("Pending work items on this pool \n")
			for work in list_for_each_entry("struct work_struct", worker_pool.worklist.address_of_(), "entry"):
				work_struct = Object(prog, 'struct work_struct', address=work.value_())
				print("work: ", hex(work.value_()), "func: ", hex(work_struct.func.value_()), "\n")
	

dump_worker_pool_states()
