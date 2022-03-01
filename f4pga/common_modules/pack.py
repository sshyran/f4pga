#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import os
import re
from f4pga.common import *
from f4pga.module import *

DEFAULT_TIMING_RPT = 'pre_pack.report_timing.setup.rpt'
DEFAULT_UTIL_RPT = 'packing_pin_util.rpt'

class PackModule(Module):
    def map_io(self, ctx: ModuleContext):
        p = file_noext(ctx.takes.eblif)
        build_dir = os.path.dirname(p)

        return {
            'net': p + '.net',
            'util_rpt': os.path.join(build_dir, DEFAULT_UTIL_RPT),
            'timing_rpt': os.path.join(build_dir, DEFAULT_TIMING_RPT)
        }

    def execute(self, ctx: ModuleContext):
        vpr_args = VprArgs(ctx.share, ctx.takes.eblif, ctx.values,
                           sdc_file=ctx.takes.sdc)
        build_dir = os.path.dirname(ctx.outputs.net)

        noisy_warnings(ctx.values.device)

        yield 'Packing with VPR...'
        vpr('pack', vpr_args, cwd=build_dir)

        og_log = os.path.join(build_dir, 'vpr_stdout.log')

        yield 'Moving/deleting files...'
        if ctx.outputs.pack_log:
            shutil.move(og_log, ctx.outputs.pack_log)
        else:
            os.remove(og_log)

        if ctx.outputs.timing_rpt:
            shutil.move(os.path.join(build_dir, DEFAULT_TIMING_RPT),
                        ctx.outputs.timing_rpt)
        if ctx.outputs.util_rpt:
            shutil.move(os.path.join(build_dir, DEFAULT_UTIL_RPT),
                        ctx.outputs.util_rpt)

    def __init__(self, _):
        self.name = 'pack'
        self.no_of_phases = 2
        self.takes = [
            'eblif',
            'sdc?'
        ]
        self.produces = [
            'net',
            'util_rpt',
            'timing_rpt',
            'pack_log!'
        ]
        self.values = [
            'device',
        ] + vpr_specific_values()

ModuleClass = PackModule
