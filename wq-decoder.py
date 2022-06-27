#!/usr/bin/env drgn
# SPDX-License-Identifier: GPL-3.0-or-later

"""Dump workqueue and worker_pool states"""

import os
import sys
from drgn import Object
from drgn.helpers.linux.idr import idr_for_each
from drgn.helpers.linux.list import *

# Copied from kernel source (workqueue.c)

WQ_UNBOUND              = 1 << 1 # not bound to any cpu
WQ_FREEZABLE            = 1 << 2 # freeze during suspend
WQ_MEM_RECLAIM          = 1 << 3 # may be used for memory reclaim
WQ_HIGHPRI              = 1 << 4 # high priority
WQ_CPU_INTENSIVE        = 1 << 5 # cpu intensive workqueue
WQ_SYSFS                = 1 << 6 # visible in sysfs, see wq_sysfs_register()
WQ_POWER_EFFICIENT      = 1 << 7

__WQ_DRAINING           = 1 << 16 # internal: workqueue is draining
__WQ_ORDERED            = 1 << 17 # internal: workqueue is ordered
__WQ_LEGACY             = 1 << 18 # internal: create*_workqueue()
__WQ_ORDERED_EXPLICIT   = 1 << 19 # internal: alloc_ordered_workqueue()


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
			print("\tThere are no pending work items on this pool \n")
		else:
			print("\tPending work items on this pool \n")
			for work in list_for_each_entry("struct work_struct", worker_pool.worklist.address_of_(), "entry"):
				work_struct = Object(prog, 'struct work_struct', address=work.value_())
				print("\t\twork: ", hex(work.value_()), "func: ", hex(work_struct.func.value_()), "\n")
	


def dump_workqueue_states():
	for wq in list_for_each_entry("struct workqueue_struct", prog['workqueues'].address_of_(), "list"):
		workqueue = Object(prog, "struct workqueue_struct", address=wq.value_())
		print("workqueue: ", workqueue.name.string_())
		if(workqueue.flags.value_() & WQ_UNBOUND):
			print("\tWQ_UNBOUND\n")
		if(workqueue.flags.value_() & WQ_FREEZABLE):
			print("\tWQ_FREEZABLE\n")
		if(workqueue.flags.value_() & WQ_MEM_RECLAIM):
			print("\tWQ_MEM_RECLAIM\n")
		if(workqueue.flags.value_() & WQ_HIGHPRI):
			print("\tWQ_HIGHPRI\n")
		if(workqueue.flags.value_() & WQ_CPU_INTENSIVE):
			print("\tWQ_CPU_INTENSIVE\n")
		if(workqueue.flags.value_() & WQ_SYSFS):
			print("\tWQ_SYSFS\n")
		if(workqueue.flags.value_() & WQ_POWER_EFFICIENT):
			print("\tWQ_POWER_EFFICIENT\n")
		if(workqueue.flags.value_() & __WQ_DRAINING):
			print("\t__WQ_DRAINING\n")
		if(workqueue.flags.value_() & __WQ_ORDERED):
			print("\t__WQ_ORDERED\n")
		if(workqueue.flags.value_() & __WQ_LEGACY):
			print("\t__WQ_LEGACY\n")
		if(workqueue.flags.value_() & __WQ_ORDERED_EXPLICIT):
			print("\t__WQ_ORDERED_EXPLICIT\n")

dump_worker_pool_states()
dump_workqueue_states()
