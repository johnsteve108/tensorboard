# Copyright 2020 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Unit tests for `tensorboard.data.server_ingester`."""

import os
import subprocess
import threading
import time
from unittest import mock

import grpc

from tensorboard import test as tb_test
from tensorboard.data import grpc_provider
from tensorboard.data import server_ingester
from tensorboard.util import grpc_util


class ExistingServerDataIngesterTest(tb_test.TestCase):
    def test(self):
        addr = "localhost:6806"
        with mock.patch.object(grpc, "secure_channel", autospec=True):
            ingester = server_ingester.ExistingServerDataIngester(
                addr,
                channel_creds_type=grpc_util.ChannelCredsType.LOCAL,
            )
            ingester.start()
        self.assertIsInstance(
            ingester.data_provider, grpc_provider.GrpcDataProvider
        )


class SubprocessServerDataIngesterTest(tb_test.TestCase):
    def test(self):
        # Create a fake server binary so that the `os.path.exists` check
        # passes.
        fake_binary = os.path.join(self.get_temp_dir(), "server")
        with open(fake_binary, "wb"):
            pass

        real_popen = subprocess.Popen
        port_file = None  # value of `--port-file` to be stashed here

        # Stub out `subprocess.Popen` to write the port file.
        def fake_popen(subprocess_args, *args, **kwargs):
            def target():
                time.sleep(0.2)  # wait one cycle
                for arg in subprocess_args:
                    port_file_prefix = "--port-file="
                    if not arg.startswith(port_file_prefix):
                        continue
                    nonlocal port_file
                    port_file = arg[len(port_file_prefix) :]
                    with open(port_file, "w") as outfile:
                        outfile.write("23456\n")

            result = mock.create_autospec(real_popen, instance=True)
            result.stdin = mock.Mock()
            result.poll = lambda: None
            result.pid = 789
            threading.Thread(target=target).start()
            return result

        tilde_logdir = "~/tmp/logs"
        expanded_logdir = os.path.expanduser(tilde_logdir)
        self.assertNotEqual(tilde_logdir, expanded_logdir)

        with mock.patch.object(subprocess, "Popen", wraps=fake_popen) as popen:
            with mock.patch.object(grpc, "secure_channel", autospec=True) as sc:
                ingester = server_ingester.SubprocessServerDataIngester(
                    server_binary=fake_binary,
                    logdir=tilde_logdir,
                    reload_interval=5,
                    channel_creds_type=grpc_util.ChannelCredsType.LOCAL,
                    samples_per_plugin={
                        "scalars": 500,
                        "images": 0,
                    },
                )
                ingester.start()
        self.assertIsInstance(
            ingester.data_provider, grpc_provider.GrpcDataProvider
        )

        expected_args = [
            fake_binary,
            "--logdir=%s" % expanded_logdir,
            "--reload=5",
            "--port=0",
            "--port-file=%s" % port_file,
            "--die-after-stdin",
            "--samples-per-plugin=scalars=500,images=all",
            "--verbose",  # logging is enabled in tests
        ]
        popen.assert_called_once_with(expected_args, stdin=subprocess.PIPE)
        sc.assert_called_once_with(
            "localhost:23456", mock.ANY, options=mock.ANY
        )


if __name__ == "__main__":
    tb_test.main()
