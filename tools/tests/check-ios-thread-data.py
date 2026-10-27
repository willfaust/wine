#!/usr/bin/env python3
"""Exercise the iOS thread view against the real TEB and retained layout."""
from pathlib import Path
import os
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
header = root / "dlls/ntdll/unix/unix_private_ios.h"
source = r'''
#include <assert.h>
#include <stdlib.h>
#include "ntstatus.h"
#include "windef.h"
#include "winternl.h"
static TEB *test_teb;
#undef NtCurrentTeb
#define NtCurrentTeb() test_teb
#include "unix_private_ios.h"
int main(void)
{
    TEB *a = calloc(1, 0x10000), *b = calloc(1, 0x10000);
    struct thread_data *data;
    assert(a && b);
    assert(!get_thread_data());
    a->ClientId.UniqueThread = ULongToHandle(0x24);
    a->ClientId.UniqueProcess = ULongToHandle(0x20);
    b->ClientId.UniqueThread = ULongToHandle(0x34);
    b->ClientId.UniqueProcess = ULongToHandle(0x30);
    test_teb = a;
    data = get_thread_data();
    assert(data == ntdll_get_thread_data());
    assert(data->teb == a && data->tid == 0x24);
    data->request_fd = 17;
    data->wait_fd[1] = 19;
    assert(ntdll_get_thread_data()->request_fd == 17);
    assert(data->debug_info == (char *)((TEB32 *)((char *)a + 0x2000) + 1));
    test_teb = b;
    assert(get_thread_data()->tid == 0x34 && get_thread_data()->teb == b);
    assert(!get_thread_data()->request_fd);
    get_thread_data()->request_fd = 23;
    test_teb = a;
    assert(get_thread_data()->request_fd == 17 && get_thread_data()->wait_fd[1] == 19);
    test_teb = NULL;
    assert(!get_thread_data());
    free(a);
    free(b);
}
'''
with tempfile.TemporaryDirectory() as folder:
    c = Path(folder) / "thread.c"
    binary = Path(folder) / "thread"
    c.write_text(source)
    subprocess.run([os.environ.get("CC", "cc"), "-std=gnu11", "-fsanitize=address,undefined",
                    "-D__WINESRC__", "-DWINE_UNIX_LIB", "-DWINE_IOS", "-D_WIN64",
                    "-I" + str(root / "include"), "-I" + str(header.parent),
                    "-I" + str(header.parent.parent), str(c), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print("PASS: iOS TEB offsets, shared thread view, null TEB and separate process state")
