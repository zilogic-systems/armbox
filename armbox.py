#!/usr/bin/python
from __future__ import print_function

import re
import os
import shutil
import subprocess
import json
import tempfile
import time
import atexit
import sys

import jinja2
import bottle


html_view_tmpl = """
<!DOCTYPE html>
<html>
  <head>
    <title>Assembly program</title>
    <style>
    .title {
       text-align:center;
       font-size:150%;
       font-weight: bold;
       padding: 0.5em;
    }
    .error {
       display: inline-block;
       text-align:left;
       background-color:#EEEEEE;
       padding: 0 20px 0 20px;
    }
    .autocenter {
       margin-left: auto;
       margin-right: auto
    }
    input[type="text"] {
      font-family: monospace;
    }
    </style>
  </head>
  <body>
    <div style="width: 100%;">
      <div class="autocenter" style="width: 1000px;">
        <form action="/cgi-bin/armbox.cgi" method="post" style="width: 100%">
      <table style="width: 100%">
        <tr><td colspan="2" class="title">ARM Simulator</td><tr>
          <td colspan="2" style="text-align: center">
                <input type="text" name="instruction" size="32" value="{{ prog }}"></instruction>
                <input type="submit" value="Execute">
              </td>
            </tr>
            <tr>
              <td colspan="2" style="text-align:center">
              <div class="error"><pre>{{ error }}</pre></div></td>
        </tr>
            <tr><td class="title">Registers</td><td class="title">Memory</td></tr>
            <tr>
          <td style="padding: 0.5em">
              <table cellpadding="5" border="1" class="autocenter">
              <tr><td>R0</td><td><input type="text" name="R00" value="{{ '0x{0:08X}'.format(R00) }}" size="10"/></td>
                  <td>R1</td><td><input type="text" name="R01" value="{{ '0x{0:08X}'.format(R01) }}" size="10"/></td></tr>
              <tr><td>R2</td><td><input type="text" name="R02" value="{{ '0x{0:08X}'.format(R02) }}" size="10"/></td>
                  <td>R3</td><td><input type="text" name="R03" value="{{ '0x{0:08X}'.format(R03) }}" size="10"/></td></tr>
              <tr><td>R4</td><td><input type="text" name="R04" value="{{ '0x{0:08X}'.format(R04) }}" size="10"/></td>
                  <td>R5</td><td><input type="text" name="R05" value="{{ '0x{0:08X}'.format(R05) }}" size="10"/></td></tr>
              <tr><td>R6</td><td><input type="text" name="R06" value="{{ '0x{0:08X}'.format(R06) }}" size="10"/></td>
                  <td>R7</td><td><input type="text" name="R07" value="{{ '0x{0:08X}'.format(R07) }}" size="10"/></td></tr>
              <tr><td>R8</td><td><input type="text" name="R08" value="{{ '0x{0:08X}'.format(R08) }}" size="10"/></td>
                  <td>R9</td><td><input type="text" name="R09" value="{{ '0x{0:08X}'.format(R09) }}" size="10"/></td></tr>
              <tr><td>R10</td><td><input type="text" name="R10" value="{{ '0x{0:08X}'.format(R10) }}" size="10"/></td>
                  <td>R11</td><td><input type="text" name="R11" value="{{ '0x{0:08X}'.format(R11) }}" size="10"/></td></tr>
              <tr><td>R12</td><td><input type="text" name="R12" value="{{ '0x{0:08X}'.format(R12) }}" size="10"/></td>
                  <td>R13</td><td><input type="text" name="R13" value="{{ '0x{0:08X}'.format(R13) }}" size="10"/></td></tr>
              <tr><td>R14</td><td><input type="text" name="R14" value="{{ '0x{0:08X}'.format(R14) }}" size="10"/></td>
                  <td>R15</td><td><tt>{{ '0x{0:08X}'.format(R15) }}</tt></td></tr>
              <tr><td colspan="4">Flags:
                  <input type="checkbox" name="N" {{ 'checked' if N else '' }}/>N
                  <input type="checkbox" name="Z" {{ 'checked' if Z else '' }}/>Z
                  <input type="checkbox" name="C" {{ 'checked' if C else '' }}/>C
                  <input type="checkbox" name="V" {{ 'checked' if V else '' }}/>V</td></tr>
              </table>
              </td>
          <td style="padding: 0.5em">
              <table cellpadding="7" border="1" class="autocenter">
              <tr><td><tt>0xA00000000</tt></td>
                  <td><input type="text" name="memA0000000" value="{{ '0x{0:08X}'.format(memA0000000) }}" size="10"/></td>
                  <td><input type="text" name="memA0000004" value="{{ '0x{0:08X}'.format(memA0000004) }}" size="10"/></td>
                  <td><input type="text" name="memA0000008" value="{{ '0x{0:08X}'.format(memA0000008) }}" size="10"/></td>
                  <td><input type="text" name="memA000000C" value="{{ '0x{0:08X}'.format(memA000000C) }}" size="10"/></td>
              </tr>
              <tr><td><tt>0xA00000010</tt></td>
                  <td><input type="text" name="memA0000010" value="{{ '0x{0:08X}'.format(memA0000010) }}" size="10"/></td>
                  <td><input type="text" name="memA0000014" value="{{ '0x{0:08X}'.format(memA0000014) }}" size="10"/></td>
                  <td><input type="text" name="memA0000018" value="{{ '0x{0:08X}'.format(memA0000018) }}" size="10"/></td>
                  <td><input type="text" name="memA000001C" value="{{ '0x{0:08X}'.format(memA000001C) }}" size="10"/></td>
              </tr>
              <tr><td><tt>0xA00000020</tt></td>
                  <td><input type="text" name="memA0000020" value="{{ '0x{0:08X}'.format(memA0000020) }}" size="10"/></td>
                  <td><input type="text" name="memA0000024" value="{{ '0x{0:08X}'.format(memA0000024) }}" size="10"/></td>
                  <td><input type="text" name="memA0000028" value="{{ '0x{0:08X}'.format(memA0000028) }}" size="10"/></td>
                  <td><input type="text" name="memA000002C" value="{{ '0x{0:08X}'.format(memA000002C) }}" size="10"/></td>
              </tr>
              <tr><td><tt>0xA00000030</tt></td>
                  <td><input type="text" name="memA0000030" value="{{ '0x{0:08X}'.format(memA0000030) }}" size="10"/></td>
                  <td><input type="text" name="memA0000034" value="{{ '0x{0:08X}'.format(memA0000034) }}" size="10"/></td>
                  <td><input type="text" name="memA0000038" value="{{ '0x{0:08X}'.format(memA0000038) }}" size="10"/></td>
                  <td><input type="text" name="memA000003C" value="{{ '0x{0:08X}'.format(memA000003C) }}" size="10"/></td>
              </tr>
              <tr><td><tt>0xA00000400</tt></td>
                  <td><input type="text" name="memA0000040" value="{{ '0x{0:08X}'.format(memA0000040) }}" size="10"/></td>
                  <td><input type="text" name="memA0000044" value="{{ '0x{0:08X}'.format(memA0000044) }}" size="10"/></td>
                  <td><input type="text" name="memA0000048" value="{{ '0x{0:08X}'.format(memA0000048) }}" size="10"/></td>
                  <td><input type="text" name="memA000004C" value="{{ '0x{0:08X}'.format(memA000004C) }}" size="10"/></td>
              </tr>
              <tr><td><tt>0xA00000050</tt></td>
                  <td><input type="text" name="memA0000050" value="{{ '0x{0:08X}'.format(memA0000050) }}" size="10"/></td>
                  <td><input type="text" name="memA0000054" value="{{ '0x{0:08X}'.format(memA0000054) }}" size="10"/></td>
                  <td><input type="text" name="memA0000058" value="{{ '0x{0:08X}'.format(memA0000058) }}" size="10"/></td>
                  <td><input type="text" name="memA000005C" value="{{ '0x{0:08X}'.format(memA000005C) }}" size="10"/></td>
              </tr>
              <tr><td><tt>0xA00000060</tt></td>
                  <td><input type="text" name="memA0000060" value="{{ '0x{0:08X}'.format(memA0000060) }}" size="10"/></td>
                  <td><input type="text" name="memA0000064" value="{{ '0x{0:08X}'.format(memA0000064) }}" size="10"/></td>
                  <td><input type="text" name="memA0000068" value="{{ '0x{0:08X}'.format(memA0000068) }}" size="10"/></td>
                  <td><input type="text" name="memA000006C" value="{{ '0x{0:08X}'.format(memA000006C) }}" size="10"/></td>
              </tr>
              <tr><td><tt>0xA00000070</tt></td>
                  <td><input type="text" name="memA0000070" value="{{ '0x{0:08X}'.format(memA0000070) }}" size="10"/></td>
                  <td><input type="text" name="memA0000074" value="{{ '0x{0:08X}'.format(memA0000074) }}" size="10"/></td>
                  <td><input type="text" name="memA0000078" value="{{ '0x{0:08X}'.format(memA0000078) }}" size="10"/></td>
                  <td><input type="text" name="memA000007C" value="{{ '0x{0:08X}'.format(memA000007C) }}" size="10"/></td>
              </tr>
              </tr>
              </table>
              </td>
            </tr>
      </table>
    </form>
    <p style="text-align:center">
    Powered By: Qemu | GNU Toolchain | Python | Bottle
    </p>
    </div>
    </div>
  </body>
</html>
"""

build_script = """
set -e
arm-none-eabi-as prog.s -o prog.o
arm-none-eabi-ld -Ttext=0x0 -o prog.elf prog.o
arm-none-eabi-objcopy -O  binary prog.elf prog.bin
dd if=/dev/zero of=flash.bin bs=4096 count=4096 > /dev/null 2>&1
dd if=prog.bin of=flash.bin bs=4096 conv=notrunc > /dev/null 2>&1
exec qemu-system-arm -M connex -pflash flash.bin -nographic -qmp stdio
"""

cmd_qmp_enable = '{ "execute": "qmp_capabilities" }'
cmd_register_dump = '{ "execute": "human-monitor-command", "arguments": {"command-line": "info registers"} }'
cmd_memory_dump = '{ "execute": "human-monitor-command", "arguments": {"command-line": "xp /32w 0xA0000000"} }'
cmd_quit = '{ "execute": "quit" }'

info_regs_default = """
R00=00000000 R01=00000000 R02=00000009 R03=00000000
R04=00000000 R05=00000000 R06=00000000 R07=00000000
R08=00000000 R09=00000000 R10=00000000 R11=00000000
R12=00000000 R13=00000000 R14=00000000 R15=00000000
PSR=40000000 ---- A svc32
"""

mem_dump_default = ("0000000000000000: 0x00000000 0x00000000 0x00000000 0x00000000\n"
                    "0000000000000000: 0x00000000 0x00000000 0x00000000 0x00000000\n"
                    "0000000000000000: 0x00000000 0x00000000 0x00000000 0x00000000\n"
                    "0000000000000000: 0x00000000 0x00000000 0x00000000 0x00000000\n"
                    "0000000000000000: 0x00000000 0x00000000 0x00000000 0x00000000\n"
                    "0000000000000000: 0x00000000 0x00000000 0x00000000 0x00000000\n"
                    "0000000000000000: 0x00000000 0x00000000 0x00000000 0x00000000\n"
                    "0000000000000000: 0x00000000 0x00000000 0x00000000 0x00000000\n")


asm_prog_tmpl = """
  .global _start
  b _start
mem:
  .4byte {{ memA0000000 }}, {{ memA0000004 }}, {{ memA0000008 }}, {{ memA000000C }}
  .4byte {{ memA0000010 }}, {{ memA0000014 }}, {{ memA0000018 }}, {{ memA000001C }}
  .4byte {{ memA0000020 }}, {{ memA0000024 }}, {{ memA0000028 }}, {{ memA000002C }}
  .4byte {{ memA0000030 }}, {{ memA0000034 }}, {{ memA0000038 }}, {{ memA000003C }}
  .4byte {{ memA0000040 }}, {{ memA0000044 }}, {{ memA0000048 }}, {{ memA000004C }}
  .4byte {{ memA0000050 }}, {{ memA0000054 }}, {{ memA0000058 }}, {{ memA000005C }}
  .4byte {{ memA0000060 }}, {{ memA0000064 }}, {{ memA0000068 }}, {{ memA000006C }}
  .4byte {{ memA0000070 }}, {{ memA0000074 }}, {{ memA0000078 }}, {{ memA000007C }}

  .align
_start:

  ldr r0, =0xA0000000
  ldr r1, =mem
  mov r2, #64

repeat:
  ldr r3, [r1], #4
  str r3, [r0], #4
  subs r2, r2, #1
  bne repeat

  ldr r0, ={{ PSR }}
  msr cpsr_f, r0

  ldr r0, ={{ R00 }}
  ldr r1, ={{ R01 }}
  ldr r2, ={{ R02 }}
  ldr r3, ={{ R03 }}
  ldr r4, ={{ R04 }}
  ldr r5, ={{ R05 }}
  ldr r6, ={{ R06 }}
  ldr r7, ={{ R07 }}
  ldr r8, ={{ R08 }}
  ldr r9, ={{ R09 }}
  ldr r10, ={{ R10 }}
  ldr r11, ={{ R11 }}
  ldr r12, ={{ R12 }}
  ldr r13, ={{ R13 }}
  ldr r14, ={{ R14 }}

  {{ inst }}
__stop: b __stop

"""

reg_keys = set("R{0:02d}".format(i) for i in range(15))
mem_keys = set("mem{0:08X}".format(i) for i in range(0xA0000000, 0xA0000080, 4))
flag_keys = set(["N", "Z", "C", "V"])
state_keys = reg_keys | mem_keys | flag_keys


def run_prog(instruction, state, path):
    with open(os.path.join(path, "prog.s"), "w") as fp:
        template = jinja2.Template(asm_prog_tmpl)
        prog = template.render(inst=instruction, **state)
        # print(prog)
        fp.write(prog)

    with open(os.path.join(path, "build.sh"), "w") as fp:
        fp.write(build_script)

    proc = subprocess.Popen(["bash", "build.sh"], cwd=path,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    time.sleep(1)
    cmd = (cmd_qmp_enable
           + cmd_register_dump
           + cmd_memory_dump
           + cmd_quit)
    output, error = proc.communicate(cmd.encode("utf-8"))

    error = error.decode("utf-8")
    output = output.decode("utf-8")

    if proc.returncode != 0:
        error += "\nExecution failed with error code {0}".format(proc.returncode)
        return state, error

    output = output.splitlines()
    info_regs = json.loads(output[2])["return"]
    mem_dump = json.loads(output[3])["return"]

    reg_re = re.compile("(...)=(........)")
    for match in reg_re.findall(info_regs):
        state[match[0]] = int(match[1], 16)

    psr = state["PSR"]
    state["N"] = 1 if psr & (1 << 31) else 0
    state["Z"] = 1 if psr & (1 << 30) else 0
    state["C"] = 1 if psr & (1 << 29) else 0
    state["V"] = 1 if psr & (1 << 28) else 0

    mem_re = re.compile("(................): 0x(........) 0x(........) 0x(........) 0x(........)")
    for match in mem_re.findall(mem_dump):
        addr = int(match[0], 16)
        state["mem{0:08X}".format(addr + 0)] = int(match[1], 16)
        state["mem{0:08X}".format(addr + 4)] = int(match[2], 16)
        state["mem{0:08X}".format(addr + 8)] = int(match[3], 16)
        state["mem{0:08X}".format(addr + 12)] = int(match[4], 16)

    return state, error


def get_form_state(form):
    instruction = "mov r1, #1"
    instruction = form.get("instruction", instruction)

    state = {}
    for key in state_keys:
        if key in flag_keys:
            state[key] = 1 if form.get(key, "off") == "on" else 0
        else:
            try:
                state[key] = int(form.get(key, "0"), 0)
            except ValueError:
                state[key] = 0

    state["PSR"] = state["N"] << 31 | state["Z"] << 30 | state["C"] << 29 | state["V"] << 28
    state["R15"] = 0

    return instruction, state


def main(form):
    instruction, state = get_form_state(form)
    # print(instruction, state)

    path = None
    try:
        path = tempfile.mkdtemp()
        state, error = run_prog(instruction, state, path)
    finally:
        if path:
            shutil.rmtree(path)

    # print(error, state)

    template = jinja2.Template(html_view_tmpl)
    html = template.render(prog=instruction, error=error, **state)
    return html


@bottle.route("/", method="GET")
def get_main():
    return main(bottle.request.GET)


@bottle.route("/", method="POST")
def post_main():
    return main(bottle.request.POST)


if __name__ == "__main__":
    bottle.debug(True)
    bottle.run(server="cgi")
