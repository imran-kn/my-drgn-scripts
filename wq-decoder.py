#!/usr/bin/env drgn
# SPDX-License-Identifier: GPL-3.0-or-later

"""Dump workqueue and worker_pool states"""

import os
import sys
from drgn import Object
from drgn.helpers.linux.idr import idr_for_each

def dump_worker_pool_states():
	for elem in idr_for_each(prog['worker_pool_idr'].address_of_()):
		worker_pool_address = elem[1].value_()
		worker_pool = Object(prog, 'struct worker_pool', address=worker_pool_address)
		print("worker_pool: ", hex(worker_pool_address), " id: ", worker_pool.id.value_(), " cpu: ", worker_pool.cpu.value_(), "\n")
	

dump_worker_pool_states()
